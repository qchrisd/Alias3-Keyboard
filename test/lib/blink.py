from machine import Pin
from utime import sleep

def init_pin(pin_number, 
             mode=Pin.OUT):
    return Pin(pin_number, mode)

def blink_led(pin, 
              delay = 1):
    print("LED starts flashing...")
    while True:
        try:
            pin.toggle()
            sleep(delay) # sleep 1sec
        except KeyboardInterrupt:
            break
    pin.off()
    print("Finished.")