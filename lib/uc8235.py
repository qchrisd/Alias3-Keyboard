

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
FULL_WHITE = [0xFF] * (EPD_WIDTH_BYTES * EPD_HEIGHT)
FULL_BLACK = [0x00] * (EPD_WIDTH_BYTES * EPD_HEIGHT)


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
        self.cs.value(1)
    
    def send_data(self, data:list):
        self.cs.value(0)
        self.dc.value(1)
        for i in range(0, len(data)):
            self.spi.write(bytes([data[i]]))
            time.sleep_ms(1)
        self.cs.value(1)

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

        self.write_to_buffer(FULL_WHITE)
        self.send_command(DISPLAY_REFRESH)
        self.wait_until_idle()

    # Clear screen (white)
    def write_to_buffer(self, buffer:list):
        print("  Starting clear to white...")
        self.send_command(DISPLAY_START_TRANSMISSION_1)
        self.send_data(buffer)
        print(f"  Data transfered.")
        
















    # Send command with optional data
    def send_command_with_data(self, cmd, data=None):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytearray([cmd]))  # command byte

        if data is not None:
            self.dc.value(1)
            if isinstance(data, int):
                self.spi.write(bytearray([data]))
            else:
                # ensure bytes for SPI, write in chunks
                for i in range(0, len(data), SPI_CHUNK_SIZE):
                    chunk = data[i:i + SPI_CHUNK_SIZE]
                    if isinstance(chunk, list):
                        chunk = bytearray(chunk)
                    self.spi.write(chunk)
        self.cs.value(1)

    # Wait for BUSY to go low (panel idle)
    def wait_until_idle(self, timeout_ms=5000):
        start = time.ticks_ms()
        while self.busy.value() == 0:  # BUSY active low
            if time.ticks_diff(time.ticks_ms(), start) > timeout_ms:
                raise RuntimeError("EPD busy timeout")
            time.sleep_ms(10)

    # # Panel initialization
    # def init(self):
    #     # POWER_SETTING
    #     self.send_command_with_data(0x01, bytearray([0x03, 0x00, 0x2B, 0x2B, 0x09]))
    #     self.send_command_with_data(0x04)  # POWER_ON
    #     self.wait_until_idle()

    #     # PANEL_SETTING
    #     self.send_command_with_data(0x00, 0x1F)

    #     # PLL_CONTROL
    #     self.send_command_with_data(0x30, 0x3C)

    #     # RESOLUTION
    #     self.send_command_with_data(0x61, bytearray([
    #         (EPD_WIDTH >> 8) & 0xFF,
    #         EPD_WIDTH & 0xFF,
    #         (EPD_HEIGHT >> 8) & 0xFF,
    #         EPD_HEIGHT & 0xFF
    #     ]))

    #     # GATE driving
    #     self.send_command_with_data(0x03, bytearray([
    #         (EPD_HEIGHT - 1) & 0xFF,
    #         ((EPD_HEIGHT - 1) >> 8) & 0xFF,
    #         0x00
    #     ]))

    #     # DATA_ENTRY_MODE
    #     self.send_command_with_data(0x11, 0x03)

    #     # VCOM AND DATA INTERVAL
    #     self.send_command_with_data(0x50, 0x97)

    #     # VCOM DC
    #     self.send_command_with_data(0x82, 0x12)

    #     # Minimal LUT to allow RAM writes
    #     self.send_command_with_data(0x32, bytearray([0x00] * 70))

    # Set a drawing window
    def set_window(self, x_start, y_start, x_end, y_end):
        self.send_command_with_data(0x44, bytearray([x_start // 8, x_end // 8]))
        self.send_command_with_data(0x45, bytearray([
            y_start & 0xFF, (y_start >> 8) & 0xFF,
            y_end & 0xFF, (y_end >> 8) & 0xFF
        ]))

    # Set cursor for RAM writes
    def set_cursor(self, x, y):
        self.send_command_with_data(0x4E, x // 8)
        self.send_command_with_data(0x4F, bytearray([y & 0xFF, (y >> 8) & 0xFF]))

    # Display full frame buffer (BW)
    def display_frame(self, buffer):
        if len(buffer) != EPD_WIDTH_BYTES * EPD_HEIGHT:
            raise ValueError("Invalid buffer length")

        self.set_window(0, 0, EPD_WIDTH - 1, EPD_HEIGHT - 1)
        self.set_cursor(0, 0)
        self.send_command_with_data(0x24, buffer)
        self.refresh()



    # Full refresh (legacy 0x12)
    def refresh(self):
        self.send_command_with_data(0x12)
        self.wait_until_idle()

    # Sleep mode
    def sleep(self):
        self.send_command_with_data(0x02)  # POWER_OFF
        self.wait_until_idle()
        self.send_command_with_data(0x07, 0xA5)  # DEEP_SLEEP

    # Optional test pattern (black/white stripes)
    def test_pattern(self):
        buf = bytearray(EPD_WIDTH_BYTES * EPD_HEIGHT)
        for i in range(len(buf)):
            buf[i] = 0xFF if (i // 8) % 2 else 0x00
        self.display_frame(buf)


# Example usage
if __name__ == "__main__":
    epd = UC8253()