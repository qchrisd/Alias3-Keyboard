

from machine import Pin, SPI
import time

# Display resolution
EPD_WIDTH = 416
EPD_HEIGHT = 240
EPD_WIDTH_BYTES = EPD_WIDTH // 8  # 52 bytes per row

# GPIO pins (ESP32 example)
PIN_DC = 27
PIN_RST = 26
PIN_BUSY = 25
PIN_CS = 5
PIN_SCK = 18
PIN_MOSI = 23


## Commands
# Power
POWER_ON = 0x04
POWER_ON_MEASURE = 0x05
POWER_OFF_POF = 0x02
POWER_OFF_SEQ_SETTING = 0x03
DEEP_SLEEP = 0x07
POWER_SETTING_PSR = 0x00
POWER_SETTING_PWR = 0x01
BOOSTER_SOFT_START = 0x06

# Panel
DISPLAY_START_TRANSMISSION_1 = 0x10
DATA_STOP = 0x11
DISPLAY_REFRESH = 0x12
DISPLAY_START_TRANSMISSION_2 = 0x13

# LUTs
VCOM_LUT = 0x20
W2W_LUT = 0x21
B2W_LUT = 0x22
W2B_LUT = 0x23
B2B_LUT = 0x24

# Resolution setting
RESOLUTION_SETTING = 0x61



# SPI chunk size for large buffer writes
SPI_CHUNK_SIZE = 512  # bytes

# Full white and full black buffers
FULL_WHITE = bytearray([0xFF] * (EPD_WIDTH_BYTES * EPD_HEIGHT))
FULL_BLACK = bytearray([0x00] * (EPD_WIDTH_BYTES * EPD_HEIGHT))


class UC8253:
    def __init__(self):
        # SPI setup
        self.spi = SPI(
            2,
            baudrate=200_000,  # start slow for testing
            polarity=0,
            phase=0,
            sck=Pin(PIN_SCK),
            mosi=Pin(PIN_MOSI),
            miso=None
        )
        self.spi.init()

        self.cs = Pin(PIN_CS, Pin.OUT, value=1)
        self.dc = Pin(PIN_DC, Pin.OUT, value=0)
        self.rst = Pin(PIN_RST, Pin.OUT, value=1)
        self.busy = Pin(PIN_BUSY, Pin.IN, Pin.PULL_UP)

        self.reset()
        self.init()

    # Hardware reset
    def reset(self):
        self.rst.value(1)
        time.sleep_ms(10)
        self.rst.value(0)
        time.sleep_ms(200)
        self.rst.value(1)
        time.sleep_ms(10)

    def send_command(self, cmd:int):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes([cmd]))
        time.sleep_ms(1)
        self.cs.value(1)
    
    def send_data(self, data:list|bytearray):
        self.cs.value(0)
        self.dc.value(1)
        if isinstance(data, list):
            data = bytearray(data)
        self.spi.write(data)
        time.sleep_ms(1)
        self.cs.value(1)

    def wait_until_idle(self, timeout_ms=5000):
        start = time.ticks_ms()
        while self.busy.value() == 0:  # BUSY active low
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                raise RuntimeError("EPD busy timeout")
            time.sleep_ms(10)

    def init(self):
        # Power settings
        self.send_command(POWER_SETTING_PWR)
        self.send_data([0x03, 0x10, 0x3F, 0x3F, 0x0D])
        # Panel settings
        # self.send_command(0x00)
        # self.send_data([0b11011111,
        #                 0b00001101])
        
        self.send_command(POWER_ON)
        self.wait_until_idle()
        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

        # self.write_to_buffer(FULL_WHITE)
        # self.send_command(DISPLAY_REFRESH)
        self.pattern_test()
        self.wait_until_idle()

    def write_to_buffer(self, buffer:list|bytearray):
        print("  Starting data transfer...")
        self.send_command(DISPLAY_START_TRANSMISSION_1)
        self.send_data(buffer)
        print(f"  Data transfered.")

    def pattern_test(self):
        print("Drawing stripes...")
        buf = bytearray()
        for i in range(EPD_WIDTH_BYTES * EPD_HEIGHT):
            if (i // 2) % 2 == 0:
                buf.append(0x00)  # black
            else:
                buf.append(0xFF)  # white
        self.write_to_buffer(buf)
        self.wait_until_idle()
        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()
        

# Example usage
if __name__ == "__main__":
    epd = UC8253()