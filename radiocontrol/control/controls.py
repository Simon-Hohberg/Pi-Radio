import threading
import time
import os
import RPi.GPIO as GPIO

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


class Controls:
    
    def __init__(self):
        self.station = 0;
        self.volume = 0;
        self.ext_audio_switch = 0;
        self.led1 = False;
        self.led2 = False;
        self.lock = threading.Lock()
    
    def __str__(self):
        controls_str = "     Station: " + str(self.station) + "\n" \
                     + "      Volume: " + str(self.volume) + "\n" \
                     + "Audio Source: " + str(self.ext_audio_switch) + "\n" \
                     + "       LED 1: " + ("on" if led1 else "off") + "\n" \
                     + "       LED 2: " + ("on" if led2 else "off") + "\n"
        return controls_str

class ControlsThread(threading.Thread):
    
    def __init__(self, controls):
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
            
            self.controls.station = readadc(STATION_ADC, SPICLK, SPIMOSI, SPIMISO, SPICS)
            self.controls.volume = readadc(VOLUME_ADC, SPICLK, SPIMOSI, SPIMISO, SPICS)
            self.controls.ext_audio_switch = GPIO.input(EXT_AUDIO_SWITCH)
            GPIO.output(LED_1, self.controls.led1)
            GPIO.output(LED_2, self.controls.led2)
            
            print(self.controls)
            
            self.controls.lock.release()
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
