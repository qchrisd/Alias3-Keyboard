# *****************************************************************************
# * | File        :	  Pico_ePaper-3.7.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2021-06-01
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from machine import Pin, SPI
import framebuf
import utime

# Display resolution
# ! These have been changed to accomodate the adafruit 3.7inch display
EPD_WIDTH       = 240
EPD_HEIGHT      = 416

RST_PIN         = 12
DC_PIN          = 27 # 8
CS_PIN          = 5 # 9
BUSY_PIN        = 33 # 13
SCK_PIN         = 18
MOSI_PIN        = 23

EPD_3IN7_lut_4Gray_GC =[
0x2A,0x06,0x15,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#1
0x28,0x06,0x14,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#2
0x20,0x06,0x10,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#3
0x14,0x06,0x28,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#4
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#5
0x00,0x02,0x02,0x0A,0x00,0x00,0x00,0x08,0x08,0x02,#6
0x00,0x02,0x02,0x0A,0x00,0x00,0x00,0x00,0x00,0x00,#7
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#8
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#9
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#10
0x22,0x22,0x22,0x22,0x22
]

EPD_3IN7_lut_1Gray_GC =[
0x2A,0x05,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#1
0x05,0x2A,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#2
0x2A,0x15,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#3
0x05,0x0A,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#4
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#5
0x00,0x02,0x03,0x0A,0x00,0x02,0x06,0x0A,0x05,0x00,#6
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#7
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#8
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#9
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#10
0x22,0x22,0x22,0x22,0x22
]

EPD_3IN7_lut_1Gray_DU =[
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#1
0x01,0x2A,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x0A,0x55,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#3
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#5
0x00,0x00,0x05,0x05,0x00,0x05,0x03,0x05,0x05,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#7
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#9
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,
0x22,0x22,0x22,0x22,0x22
]

EPD_3IN7_lut_1Gray_A2 =[
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#1
0x0A,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#2
0x05,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#3
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#4
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#5
0x00,0x00,0x03,0x05,0x00,0x00,0x00,0x00,0x00,0x00,#6
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#7
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#8
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#9
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,#10
0x22,0x22,0x22,0x22,0x22
]

class EPD_3in7:
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN)  # Removed PULL_UP - should use external pull-up or controller's
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        self.lut_4Gray_GC = EPD_3IN7_lut_4Gray_GC
        self.lut_1Gray_GC = EPD_3IN7_lut_1Gray_GC
        self.lut_1Gray_DU = EPD_3IN7_lut_1Gray_DU
        self.lut_1Gray_A2 = EPD_3IN7_lut_1Gray_A2
        
        self.black = 0x00
        self.white = 0xff
        self.darkgray = 0xaa
        self.grayish = 0x55
        
        
        # self.spi = SPI(2)
        self.spi = SPI(1, baudrate=1000000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
        self.spi.init()#baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        
        
        self.buffer_1Gray = bytearray(self.height * self.width // 8)
        self.buffer_4Gray = bytearray(self.height * self.width // 4)
        self.image1Gray = framebuf.FrameBuffer(self.buffer_1Gray, self.width, self.height, framebuf.MONO_HLSB)
        self.image4Gray = framebuf.FrameBuffer(self.buffer_4Gray, self.width, self.height, framebuf.GS2_HMSB)
        
        self.EPD_3IN7_1Gray_init()
        self.EPD_3IN7_1Gray_Clear()
        utime.sleep_ms(500)

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        print("Reset - Setting pin to 1")
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(200) 
        print("Reset - Set pin to 1 complete")
        print("Reset - Setting pin to 0")
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(200)
        print("Reset - Set pin to 0 complete")
        print("Reset - Setting pin to 1")
        self.digital_write(self.reset_pin, 1)
        print("Reset - Set pin to 1 complete")
        self.delay_ms(200)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)
        self.delay_ms(1)  # Small delay to ensure command is processed

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        if isinstance(data, list):
            self.spi_writebyte(data)
        else:
            self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def ReadBusy(self):
        print("e-Paper busy - waiting for completion")
        timeout = 5000  # Increased timeout from 2000 to 5000
        initial_state = self.digital_read(self.busy_pin)
        print(f"Initial busy pin state: {initial_state} (0=idle, 1=busy)")
        
        # Wait for busy pin to go LOW (0 = idle, 1 = busy)
        while(self.digital_read(self.busy_pin) == 1):      
            self.delay_ms(10)
            timeout -= 1
            if (timeout % 500 == 0):
                current_state = self.digital_read(self.busy_pin)
                print(f"Waiting... timeout remaining: {timeout}, current busy state: {current_state}")
            if (timeout <= 0):
                print("WARNING: ReadBusy timeout - display may not have completed")
                break
        self.delay_ms(200) 
        print("e-Paper busy release - display ready")
        
    def Load_LUT(self,lut):
        self.send_command(0x32)
        for count in range(0, 105):
            if lut == 0 :
                self.send_data(self.lut_4Gray_GC[count])
            elif lut == 1 :
                self.send_data(self.lut_1Gray_GC[count])
            elif lut == 2 :
                self.send_data(self.lut_1Gray_DU[count])
            elif lut == 3 :
                self.send_data(self.lut_1Gray_A2[count])
            else:
                print("There is no such lut ")
        
    def EPD_3IN7_4Gray_init(self):
        print("EPD_3IN7_4Gray_init")
        self.reset()              # SWRESET

        self.send_command(0x04)  # POWER_ON - wake from sleep
        self.delay_ms(300)
        
        self.send_command(0x12)
        self.delay_ms(300)   

        self.send_command(0x46)
        self.send_data(0xF7)
        self.delay_ms(1)
        self.send_command(0x47)
        self.send_data(0xF7)
        self.delay_ms(1)
        
        self.send_command(0x01)   # setting gaet number
        self.send_data([0xDF, 0x01, 0x00])

        self.send_command(0x03)   # set gate voltage
        self.send_data(0x00)

        self.send_command(0x04)   # set source voltage
        self.send_data([0x41, 0xA8, 0x32])

        self.send_command(0x11)   # set data entry sequence
        self.send_data(0x03)

        self.send_command(0x3C)   # set border 
        self.send_data(0x03)

        self.send_command(0x0C)   # set booster strength
        self.send_data([0xAE, 0xC7, 0xC3, 0xC0, 0xC0])

        self.send_command(0x18)   # set internal sensor on
        self.send_data(0x80)
         
        self.send_command(0x2C)   # set vcom value
        self.send_data(0x44)

        self.send_command(0x37)   # set display option, these setting turn on previous function
        self.send_data([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        self.send_command(0x44)   # setting X direction start/end position of RAM
        self.send_data([0x00, 0x00, 0x17, 0x01])

        self.send_command(0x45)   # setting Y direction start/end position of RAM
        self.send_data([0x00, 0x00, 0xDF, 0x01])

        self.send_command(0x22)   # Display Update Control 2
        self.send_data(0xCF)

    def EPD_3IN7_1Gray_init(self):
        print("EPD_3IN7_1Gray_init")
        self.reset()
        
        self.send_command(0x04)  # POWER_ON - wake from sleep
        self.delay_ms(300)
        
        self.send_command(0x12)
        self.delay_ms(300)  
        
        self.send_command(0x46)
        self.send_data(0xF7)
        self.delay_ms(1)
        self.send_command(0x47)
        self.send_data(0xF7)
        self.delay_ms(1)

        self.send_command(0x01)   # setting gate number
        self.send_data([0xDF, 0x01, 0x00])

        self.send_command(0x03)   # set gate voltage
        self.send_data(0x00)

        self.send_command(0x04)   # set source voltage
        self.send_data([0x41, 0xA8, 0x32])

        self.send_command(0x11)   # set data entry sequence
        self.send_data(0x03)

        self.send_command(0x3C)   # set border 
        self.send_data(0x03)

        self.send_command(0x0C)   # set booster strength
        self.send_data([0xAE, 0xC7, 0xC3, 0xC0, 0xC0])

        self.send_command(0x18)   # set internal sensor on
        self.send_data(0x80)
         
        self.send_command(0x2C)   # set vcom value
        self.send_data(0x44)

        self.send_command(0x37)   # set display option, these setting turn on previous function
        self.send_data([0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0x4F, 0xFF, 0xFF, 0xFF, 0xFF])

        self.send_command(0x44)   # setting X direction start/end position of RAM
        self.send_data([0x00, 0x00, 0x17, 0x01])

        self.send_command(0x45)   # setting Y direction start/end position of RAM
        self.send_data([0x00, 0x00, 0xDF, 0x01])

        self.send_command(0x22)   # Display Update Control 2
        self.send_data(0xCF)
        print("finish init")
        
    def EPD_3IN7_4Gray_Clear(self):    
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1

        self.send_command(0x49)
        self.send_data(0x00)
        self.send_command(0x4E)
        self.send_data([0x00, 0x00])
        self.send_command(0x4F)
        self.send_data([0x00, 0x00])
        
        self.send_command(0x24)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0xFF)
        
        self.send_command(0x4E)
        self.send_data([0x00, 0x00])
         
        self.send_command(0x4F)
        self.send_data([0x00, 0x00])
        
        self.send_command(0x26)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0xFF)
          
        self.Load_LUT(0)
        self.send_command(0x22)
        self.send_data(0xC7)

        self.send_command(0x20)
        self.ReadBusy()    
        
    def EPD_3IN7_1Gray_Clear(self):
        print("Clearing EPD 3.7inch 1Gray - filling with BLACK")
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1

        # Set RAM address counters to origin
        self.send_command(0x4E)
        self.send_data([0x00, 0x00])
        self.send_command(0x4F)
        self.send_data([0x00, 0x00])

        # Fill current image RAM with BLACK (0x00)
        self.send_command(0x24)
        print(f"Writing {high * wide} bytes of 0x00 to RAM (0x24)")
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(0x00)  # BLACK
        
        print("Black fill complete. Loading LUT and triggering refresh...")
        self.Load_LUT(1)
        self.send_command(0x22)
        self.send_data(0xC7)

        self.send_command(0x20)
        self.ReadBusy()
        print("EPD 3.7inch 1Gray cleared - display should be BLACK")
        
    def EPD_3IN7_4Gray_Display(self,Image):
        
        self.send_command(0x49)
        self.send_data(0x00)

        
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_data(0x00)
        
        
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x24)
        for i in range(0, 16800):
            temp3=0
            for j in range(0, 2):
                temp1 = Image[i*2+j]
                for k in range(0, 2):
                    temp2 = temp1&0x03 
                    if(temp2 == 0x03):
                        temp3 |= 0x01   # white
                    elif(temp2 == 0x00):
                        temp3 |= 0x00   # black
                    elif(temp2 == 0x02):
                        temp3 |= 0x01   # gray1
                    else:   # 0x01
                        temp3 |= 0x00   # gray2
                    temp3 <<= 1

                    temp1 >>= 2
                    temp2 = temp1&0x03 
                    if(temp2 == 0x03):   # white
                        temp3 |= 0x01;
                    elif(temp2 == 0x00):   # black
                        temp3 |= 0x00;
                    elif(temp2 == 0x02):
                        temp3 |= 0x01   # gray1
                    else:   # 0x01
                        temp3 |= 0x00   # gray2
                    
                    if (( j!=1 ) | ( k!=1 )):
                        temp3 <<= 1

                    temp1 >>= 2
                    
            self.send_data(temp3)
        # new  data
        self.send_command(0x4E)
        self.send_data(0x00)
        self.send_data(0x00)
         
        
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)
        
        self.send_command(0x26)
        for i in range(0, 16800):
            temp3=0
            for j in range(0, 2):
                temp1 = Image[i*2+j]
                for k in range(0, 2):
                    temp2 = temp1&0x03 
                    if(temp2 == 0x03):
                        temp3 |= 0x01   # white
                    elif(temp2 == 0x00):
                        temp3 |= 0x00   # black
                    elif(temp2 == 0x02):
                        temp3 |= 0x00   # gray1
                    else:   # 0x01
                        temp3 |= 0x01   # gray2
                    temp3 <<= 1

                    temp1 >>= 2
                    temp2 = temp1&0x03
                    if(temp2 == 0x03):   # white
                        temp3 |= 0x01;
                    elif(temp2 == 0x00):   # black
                        temp3 |= 0x00;
                    elif(temp2 == 0x02):
                        temp3 |= 0x00   # gray1
                    else:   # 0x01
                        temp3 |= 0x01   # gray2
                    
                    if (( j!=1 ) | ( k!=1 )):
                        temp3 <<= 1

                    temp1 >>= 2

            self.send_data(temp3)
        
        self.Load_LUT(0)
        
        self.send_command(0x22)
        self.send_data(0xC7)
        
        self.send_command(0x20)
        
        self.ReadBusy()
        
    def EPD_3IN7_1Gray_Display(self,Image):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1

        self.send_command(0x49)
        self.send_data(0x00)
        
        self.send_command(0x4E)
        self.send_data([0x00, 0x00])
        self.send_command(0x4F)
        self.send_data([0x00, 0x00])

        self.send_command(0x24)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(Image[i + j * wide])
        

        self.Load_LUT(1)
        self.send_command(0x22)
        self.send_data(0xC7)
        
        self.send_command(0x20)
        self.ReadBusy()
        
    def EPD_3IN7_1Gray_Display_Part(self,Image):
        
        high = self.height
        if( self.width % 8 == 0) :
            wide =  self.width // 8
        else :
            wide =  self.width // 8 + 1

        self.send_command(0x44)
        self.send_data([0x00, 0x00, (self.width-1) & 0xff, ((self.width-1)>>8) & 0x03])
        self.send_command(0x45)
        self.send_data([0x00, 0x00, (self.height-1) & 0xff, ((self.height-1)>>8) & 0x03])

        self.send_command(0x4E)   # SET_RAM_X_ADDRESS_COUNTER
        self.send_data([0x00, 0x00])

        self.send_command(0x4F)   # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data([0x00, 0x00])
        
        self.send_command(0x24)
        for j in range(0, high):
            for i in range(0, wide):
                self.send_data(Image[i + j * wide])

        self.Load_LUT(2)
        self.send_command(0x22)
        self.send_data(0xC7)
        self.send_command(0x20)
        self.ReadBusy()
        
    def Sleep(self):
        self.send_command(0X10)  # deep sleep
        self.send_data(0x03)
    
if __name__=='__main__':
    
    epd = EPD_3in7()
    
    epd.image1Gray.fill(0xff)
    epd.image4Gray.fill(0xff)
    
    # epd.image4Gray.text("Waveshare", 5, 10, epd.black)
    # epd.image4Gray.text("Pico_ePaper-3.7", 5, 40, epd.black)
    # epd.image4Gray.text("Raspberry Pico", 5, 70, epd.black)
    # epd.EPD_3IN7_4Gray_Display(epd.buffer_4Gray)
    # epd.delay_ms(500)
    
    # epd.image4Gray.vline(10, 90, 60, epd.black)
    # epd.image4Gray.vline(90, 90, 60, epd.black)
    # epd.image4Gray.hline(10, 90, 80, epd.black)
    # epd.image4Gray.hline(10, 150, 80, epd.black)
    # epd.image4Gray.line(10, 90, 90, 150, epd.black)
    # epd.image4Gray.line(90, 90, 10, 150, epd.black)
    # epd.EPD_3IN7_4Gray_Display(epd.buffer_4Gray)
    # epd.delay_ms(500)
    
    # epd.image4Gray.rect(10, 180, 50, 80, epd.black)
    # epd.image4Gray.fill_rect(70, 180, 50, 80, epd.black)
    # epd.EPD_3IN7_4Gray_Display(epd.buffer_4Gray)
    # epd.delay_ms(500)
   
    # epd.image4Gray.fill_rect(0, 270, 280, 30, epd.black)
    # epd.image4Gray.text('GRAY1 with black background',5, 281, epd.white)
    # epd.image4Gray.text('GRAY2 with white background',5, 311, epd.grayish)
    # epd.image4Gray.text('GRAY3 with white background',5, 341, epd.darkgray)
    # epd.image4Gray.text('GRAY4 with white background',5, 371, epd.black)
    # epd.EPD_3IN7_4Gray_Display(epd.buffer_4Gray)
    # epd.delay_ms(500)
    
    
    epd.EPD_3IN7_1Gray_init()
    for i in range(0, 10):
        print("Display number:", i)
        epd.image1Gray.fill_rect(0, 430, 280, 10, epd.white)
        epd.image1Gray.text(str(i), 136, 431, epd.black)
        epd.EPD_3IN7_1Gray_Display_Part(epd.buffer_1Gray)
    



    epd.Sleep()


