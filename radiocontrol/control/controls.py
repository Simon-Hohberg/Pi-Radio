import time
import os
import RPi.GPIO as GPIO
from math import floor, log, exp
from threading import Lock, Thread, Event
import time
import random

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 4
SPIMISO = 17
SPIMOSI = 27
SPICS = 22

EXT_AUDIO_SWITCH = 24
LEDS = 23

STATION_ADC = 0
VOLUME_ADC = 1

STATION_TOLERANCE = 40
VOLUME_TOLERANCE = 1

class Controls:

    def __init__(self, num_stations=6, num_volume_lvls=20):
        self.lock = Lock()
        self.update_callback = None
        self.num_stations = num_stations
        self.num_volume_lvls = num_volume_lvls
        # value between 1 and num_stations or 0 if no station is selected
        self.station = 1
        # volume in percent
        self.volume = 0
        self.ext_audio_source = False
        self._leds_on = False
        self._leds_blink = False
        self._leds_random = False
        self.updated = False
        self.station_updated = False
        self.volume_updated = False
        self.ext_as_updated = False

    def set_update_callback(self, update_callback):
        self.update_callback = update_callback

    def set_station(self, station):
        station_id = int(floor((station / 1023.) * (self.num_stations - 1)) + 1)
        # when the current poti position is more than the tolerance away from
        # the actual station postion no station is selected (so there is a
        # margin between the stations)
        if abs((float(station_id) / self.num_stations) * 1023 - station) > STATION_TOLERANCE:
            station_id = 0
        if station_id != self.station:
            self.station = station_id
            self.station_updated = True
        self.updated |= self.station_updated

    def set_volume(self, volume):
        scaled_volume = volume / 1023.
        new_volume = int(round( (0.417032*(2.30259 + log(0.1 + scaled_volume))) * 100))
        adjust = abs(volume - new_volume)
        if adjust > VOLUME_TOLERANCE:
            self.volume = new_volume
            self.volume_updated = True
        self.updated |= self.volume_updated

    def set_ext_audio_source(self, ext_audio_source):
        if ext_audio_source != self.ext_audio_source:
            self.ext_audio_source = ext_audio_source
            self.ext_as_updated = True
        self.updated |= self.ext_as_updated

    def set_leds_on(self):
        self._leds_on = True
        self._leds_blink = False
        self._leds_random = False

    def set_leds_off(self):
        self._leds_on = False
        self._leds_blink = False
        self._leds_random = False

    def set_leds_blink(self):
        self._leds_on = False
        self._leds_blink = True
        self._leds_random = False

    def set_leds_random(self):
        self._leds_on = False
        self._leds_blink = False
        self._leds_random = True

    def notify(self):
        if self.updated:
            self.updated = False
            if self.update_callback != None:
                self.update_callback()
                self.volume_updated = False
                self.station_updated = False
                self.ext_as_updated = False

    def __str__(self):
        controls_str = "     Station: " + str(self.station) + "\n" \
                     + "      Volume: " + str(self.volume) + "\n" \
                     + "Audio Source: " + ("external" if self.ext_audio_source else "radio") + "\n" \
                     + "        LEDs: " + ("on" if self._leds_on else "blinking" if self._leds_blink else "random" if self._leds_random else "off") + "\n"
        return controls_str


PATTERN_BLINK = 0
PATTERN_RANDOM = 1

class PatternThread(Thread):

    def __init__(self, pattern=PATTERN_BLINK):
        Thread.__init__(self)
        self._stop = Event()
        self._is_running = False
        self._pattern = pattern

    def run(self):
        self._is_running = True
        # create PWM at 50Hz for LEDs
        pwm = GPIO.PWM(LEDS, 50)
        # start PWM with initial duty cycle of 0 (LEDs turned off)
        pwm.start(0)
        if self._pattern is PATTERN_BLINK:
            while not self._stop.is_set():
                # brighten and darken LEDs with short pause between each step
                # i goes from 0 to 100 to 0 again
                for i in [ step if step <= 100 else 200-step for step in range(200)]:
                    pwm.ChangeDutyCycle(i)
                    time.sleep(0.02)
        elif self._pattern is PATTERN_RANDOM:
            while not self._stop.is_set():
                pwm.ChangeDutyCycle(random.randint(10, 100))
                time.sleep(0.1)
        pwm.stop()
        # reset event
        self._stop.clear()
        self._is_running = False

    def stop(self):
        self._stop.set()

    def is_running(self):
        return self._is_running

    def set_pattern(self, pattern):
        self._pattern = pattern


class ControlsThread(Thread):

    def __init__(self, controls):
        Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        # set up the SPI interface pins
        GPIO.setup(SPIMOSI, GPIO.OUT)
        GPIO.setup(SPIMISO, GPIO.IN)
        GPIO.setup(SPICLK, GPIO.OUT)
        GPIO.setup(SPICS, GPIO.OUT)

        GPIO.setup(LEDS, GPIO.OUT)
        GPIO.setup(EXT_AUDIO_SWITCH, GPIO.IN)

        self._controls = controls
        self._pattern_thread = PatternThread()

    def run(self):
        while True:

            # > lock
            self._controls.lock.acquire()

            # read station, volume and audio source switch
            self._controls.set_station(readadc(STATION_ADC))
            self._controls.set_volume(readadc(VOLUME_ADC))
            self._controls.set_ext_audio_source(GPIO.input(EXT_AUDIO_SWITCH))
            # set LEDs
            if (self._controls._leds_blink or self._controls._leds_random) and not self._pattern_thread.is_running():
                self._pattern_thread.set_pattern(PATTERN_BLINK if self._controls._leds_blink else PATTERN_RANDOM if self._controls._leds_random else PATTERN_BLINK)
                self._pattern_thread.start()
            elif not self._controls._leds_blink and not self._controls._leds_random:
                # stop blinking
                if self._pattern_thread.is_running():
                    self._pattern_thread.stop()
                    self._pattern_thread = PatternThread()
                # turn LEDs on or off
                GPIO.output(LEDS, self._controls._leds_on)

            # print(self._controls)

            # < release
            self._controls.lock.release()

            self._controls.notify()
            time.sleep(0.1)


# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        
        clockpin = SPICLK
        mosipin = SPIMOSI
        misopin = SPIMISO
        cspin = SPICS
        
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout
