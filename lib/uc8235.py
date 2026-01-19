

from machine import Pin, SPI
import time
import gc

# Display resolution
EPD_WIDTH = 240
EPD_HEIGHT = 416
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

LUT_VCOM_NO_FLASH = bytearray([
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00,
] + [0x00] * 20)
LUT_W2W_NO_FLASH = bytearray([0x00] * 30)
LUT_B2B_NO_FLASH = bytearray([0x00] * 30)
LUT_W2B_NO_FLASH = bytearray([
    0b00010001,  # Phase 1: VSL, enable
    0x01,        # 1 frame
    0x00,        # end
] + [0x00] * 27)
LUT_B2W_NO_FLASH = bytearray([
    0b00100010,  # Phase 1: VSH, enable
    0x01,        # 1 frame
    0x00,
] + [0x00] * 27)

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
        self.BUF_OLD = 1
        self.BUF_NEW = 2
        self.frame_old = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
        self.frame_new = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
        self.refresh_counter = 0

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

    def refresh_full(self):
        self.send_command(POWER_ON)
        self.wait_until_idle()

        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

    def refresh_no_flash(self):
        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

    def load_no_flash_lut(self):
        # Tell UC8253 to use register LUTs instead of OTP
        self.send_command(POWER_SETTING_PSR)
        self.send_data([0b00001111])  # REG_LUT = 1
        self.send_data([0b00001101])

        # Upload LUTs
        self.send_command(VCOM_LUT)
        self.send_data(LUT_VCOM_NO_FLASH)

        self.send_command(W2W_LUT)
        self.send_data(LUT_W2W_NO_FLASH)

        self.send_command(B2W_LUT)
        self.send_data(LUT_B2W_NO_FLASH)

        self.send_command(W2B_LUT)
        self.send_data(LUT_W2B_NO_FLASH)

        self.send_command(B2B_LUT)
        self.send_data(LUT_B2B_NO_FLASH)

    def switch_buffer(self):
        if self.buffer_current == 1:
            self.buffer_current = 2
        else:
            self.buffer_current = 1
        print(f"  Switched to buffer {self.buffer_current}.")

    def write_new_buffer(self, 
                         buffer:list|bytearray):
        print(f"  Starting data transfer to buffer BUF_NEW...")
        self.send_command(DISPLAY_START_TRANSMISSION_2)
        time.sleep_ms(1)
        self.send_data(buffer)
        time.sleep_ms(1)
        del buffer
        gc.collect()
        print(f"  Data transfered.")
        self.refresh_counter += 1

    def write_old_buffer(self, 
                        buffer:list|bytearray):
        print(f"  Starting data transfer to buffer BUF_OLD...")
        self.send_command(DISPLAY_START_TRANSMISSION_1)
        time.sleep_ms(1)
        self.send_data(buffer)
        del buffer
        gc.collect()
        print(f"  Data transfered.")
        self.refresh_counter += 1

    def write_to_buffer(self, 
                        buffer:list|bytearray,
                        buffer_no:int|None = None):
        if buffer_no is None:
            buffer_no = self.BUF_NEW
        print(f"  Starting data transfer to buffer {buffer_no}...")
        if buffer_no != self.BUF_OLD:
            self.send_command(DISPLAY_START_TRANSMISSION_2)
            time.sleep_ms(1)
            self.send_data(buffer)
            time.sleep_ms(1)
            self.refresh_no_flash()
        print(f"  Starting data transfer to buffer 1...")
        self.send_command(DISPLAY_START_TRANSMISSION_1)
        time.sleep_ms(1)
        self.send_data(buffer)
        del buffer
        gc.collect()
        print(f"  Data transfered.")

    def vertical_stripes(self):
        self.frame_new = bytearray()
        for x in range(EPD_WIDTH_BYTES*EPD_HEIGHT):
            self.frame_new.extend([0x0f])
        self.write_new_buffer(self.frame_new)
        gc.collect()

    def horizontal_stripes(self):
        self.frame_new = bytearray()
        row = True
        for i in range(EPD_HEIGHT):
            if row == 0:
                self.frame_new.extend([0x00] * EPD_WIDTH_BYTES)  # black row
            else:
                self.frame_new.extend([0xFF] * EPD_WIDTH_BYTES)  # white row
            if i % 4 == 0:
                row = not row
        self.write_new_buffer(self.frame_new)
        gc.collect()

    def test_pattern(self):
        print("Writing horizontal stripes...")
        self.horizontal_stripes()
        self.refresh_no_flash()
        print("Screen written.")

        print("Writing vertical stripes...")
        self.vertical_stripes()
        self.refresh_no_flash()
        print("Screen written.")

        print("Writing horizontal stripes...")
        self.horizontal_stripes()
        self.refresh_no_flash()
        print("Screen written.")


    def init(self):
        # Power settings
        self.send_command(POWER_SETTING_PWR)
        self.send_data([0x03, 0x10, 0x3F, 0x3F, 0x0D])
        
        self.send_command(POWER_ON)
        self.wait_until_idle()

        # Clear panel
        self.write_old_buffer(FULL_BLACK)
        self.write_new_buffer(FULL_WHITE)
        self.refresh_full()

        # Set differential LUTs
        self.load_no_flash_lut()
        print("UC8253 initialized.")
        

# Example usage
if __name__ == "__main__":
    epd = UC8253()
    epd.test_pattern()