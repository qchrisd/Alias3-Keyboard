"""The main driver for running the epaper keyboard through ESP32."""

import lib.uc8235 as uc8235

def main():
    display = uc8235.UC8253()
    display.test_pattern()
    display.maintenance_full_refresh()

if __name__ == "__main__":
    main()