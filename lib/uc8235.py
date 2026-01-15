"""This is a driver for the UC8235 based ePaper displays.
author: Chris Quartararo
"""

from machine import Pin, SPI

# Display resolution
EPD_WIDTH = 416
EPD_HEIGHT = 240
EPD_WIDTH_BYTES = EPD_WIDTH // 8  # 52 total bytes per row


# Pin assignments for ESP32
RST_PIN = 12
DC_PIN = 27
CS_PIN = 5
BUSY_PIN = 33
SCK_PIN = 18
MOSI_PIN = 23


# Global color constants
BLACK = 0x00
WHITE = 0xFF


class UC8235:
    def __init__(self):
        pass