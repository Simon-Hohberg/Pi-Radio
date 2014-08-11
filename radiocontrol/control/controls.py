import time
import os
import RPi.GPIO as GPIO
from math import floor
from threading import Lock, Thread

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 4
SPIMISO = 17
SPIMOSI = 27
SPICS = 22

EXT_AUDIO_SWITCH = 18
LED_1 = 23
LED_2 = 24

STATION_ADC = 0
VOLUME_ADC = 1

STATION_TOLERANCE = 20
VOLUME_TOLERACE = 5

class Controls:
    
    def __init__(self, num_stations=10, num_volume_lvls=20):
        self.lock = Lock()
        self.update_callback = None
        self.num_stations = num_stations
        self.num_volume_lvls = num_volume_lvls
        # value between 1 and num_stations or 0 if no station is selected
        self.station = 1
        # volume in percent
        self.volume = 0
        self.ext_audio_source = False
        self.led1 = False
        self.led2 = False
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
        adjust = abs(volume - self.volume * 1023./100)
        if adjust > VOLUME_TOLERACE:
            self.volume = int(round(volume * 100. / 1023))
            self.volume_updated = True
        self.updated |= self.volume_updated
    
    def set_ext_audio_source(self, ext_audio_source):
        if ext_audio_source != self.ext_audio_source:
            self.ext_audio_source = ext_audio_source
            self.ext_as_updated = True
        self.updated |= self.ext_as_updated
    
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
                     + "       LED 1: " + ("on" if self.led1 else "off") + "\n" \
                     + "       LED 2: " + ("on" if self.led2 else "off") + "\n"
        return controls_str


class ControlsThread(Thread):
    
    def __init__(self, controls):
        Thread.__init__(self)
        GPIO.setmode(GPIO.BCM)
        # set up the SPI interface pins
        GPIO.setup(SPIMOSI, GPIO.OUT)
        GPIO.setup(SPIMISO, GPIO.IN)
        GPIO.setup(SPICLK, GPIO.OUT)
        GPIO.setup(SPICS, GPIO.OUT)
        
        GPIO.setup(LED_1, GPIO.OUT)
        GPIO.setup(LED_2, GPIO.OUT)
        GPIO.setup(EXT_AUDIO_SWITCH, GPIO.IN)
        
        self.controls = controls
    
    def run(self):
        while True:
            
            self.controls.lock.acquire()
            
            self.controls.set_station(readadc(STATION_ADC))
            self.controls.set_volume(readadc(VOLUME_ADC))
            self.controls.set_ext_audio_source(GPIO.input(EXT_AUDIO_SWITCH))
            GPIO.output(LED_1, self.controls.led1)
            GPIO.output(LED_2, self.controls.led2)
            
 #           print(self.controls)
            
            self.controls.lock.release()
            
            self.controls.notify()
            time.sleep(0.5)


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
