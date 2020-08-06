from time import sleep
from pynq.overlays.base import BaseOverlay

base = BaseOverlay("base.bit")

for led in base.leds:
    led.on()

def led_on():
    for led in base.leds:
        led.on()

def led_off():
    for led in base.leds:
        led.off()