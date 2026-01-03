"""The main driver for running the epaper keyboard through ESP32."""

# import lib.epd
from lib.blink import init_pin, blink_led
import sys

pin = init_pin(2)  # Initialize pin 2 for LED

modules = sys.modules.keys()
if modules:
    blink_led(pin, delay=2)
else:
    blink_led(pin, delay=0.1)