from machine import Pin, PWM, I2C
import time
import utime
import gc
from time import sleep
from micropython import const
import framebuf

class PIN:
    def __init__(self):pass
    def RGB(self,r_pin,g_pin,b_pin,r=255,g=255,b=255):
        colors = [min(255, c) for c in [r, g, b]]
        pwm_channels = [PWM(Pin(p)) for p in [r_pin,g_pin,b_pin]]
        for p in pwm_channels:p.freq(1000)
        for p, c in zip(pwm_channels, colors):p.duty_u16(65535 - int(c * 257))
    def STATE(self,pin):return Pin(pin, Pin.OUT)

# Register definitions
SET_DISP = const(0xAE)
SET_MEM_ADDR = const(0x20)
SET_COL_ADDR = const(0x21)
SET_PAGE_ADDR = const(0x22)
SET_CONTRAST = const(0x81)

class OLED(framebuf.FrameBuffer):
    def __init__(self):
        self.i2c=I2C(1, scl=Pin(27), sda=Pin(26), freq=200000)
        width,height,self.addr=128,64,0x3C
        self.buffer = bytearray((height // 8) * width)
        super().__init__(self.buffer, width, height, framebuf.MONO_VLSB)
        cmds = [ SET_DISP | 0x00, SET_MEM_ADDR, 0x00, SET_COL_ADDR, 0, 128 - 1, SET_PAGE_ADDR, 0, (height // 8) - 1, SET_CONTRAST, 0xFF, SET_DISP | 0x01 ]
        for cmd in cmds:self.i2c.writeto(self.addr, bytearray([0x80, cmd]))
        self.clear()
       
    def show(self):
        self.i2c.writeto(self.addr, bytearray([0x40]) + self.buffer)
    
    def clear(self):
        self.fill(0)
        self.show()

def main():
    oled = OLED()
    fb = framebuf.FrameBuffer(bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"), 32, 32, framebuf.MONO_HLSB)
    oled.blit(fb, 96, 0)
    oled.text("viswa", 5, 5)
    oled.text("Pico", 5, 15)
    oled.show()


#LCD 16x2
class LcdApi:

    def __init__(self,sda_pin=0,scl_pin=1,freq=400000):
        self.i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin), freq=freq)
        self.i2c_addr = self.i2c.scan()[0]
        self.num_lines = 2
        self.num_columns = 16
        self.cursor_x = 0
        self.cursor_y = 0
        self.implied_newline = False
        self.backlight = True
        self.backlight_on()
        self.display_on()
        self.clear()
        self.hide_cursor()
        self.clear()
        
    def clear(self):self.hal_write_command(0x01);self.hal_write_command(0x02);self.cursor_x = 0;self.cursor_y = 0
    def show_cursor(self):self.hal_write_command(0x08 | 0x04 |0x02)
    def hide_cursor(self):self.hal_write_command(0x08 | 0x04)
    def blink_cursor_on(self):self.hal_write_command(0x08 | 0x04 |0x02 | 0x01)
    def blink_cursor_off(self):self.hal_write_command(0x08 | 0x04 |0x02)
    def display_on(self):self.hal_write_command(0x08 | 0x04)
    def display_off(self):self.hal_write_command(0x08)
    def backlight_on(self):self.backlight = True
    def backlight_off(self):self.backlight = False

    def move_to(self, cursor_x, cursor_y):
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        addr = cursor_x & 0x3f
        if cursor_y & 1:addr += 0x40
        if cursor_y & 2:addr += self.num_columns
        self.hal_write_command(0x80 | addr)

    def write(self, string):
        for char in string:
            if char == '\n':
                if self.implied_newline:pass
                else:self.cursor_x = self.num_columns
            else:
                self.hal_write_data(ord(char))
                self.cursor_x += 1
            if self.cursor_x >= self.num_columns:
                self.cursor_x = 0
                self.cursor_y += 1
                self.implied_newline = (char != '\n')
            if self.cursor_y >= self.num_lines:
                self.cursor_y = 0
            self.move_to(self.cursor_x, self.cursor_y)

    def custom_char(self, location, charmap):
        location &= 0x7
        self.hal_write_command(0x40 | (location << 3))
        time.sleep_us(40)
        for i in range(8):self.hal_write_data(charmap[i]);time.sleep_us(40)
        self.move_to(self.cursor_x, self.cursor_y)

    def hal_write_command(self, cmd):
        byte = ((self.backlight << 3) |(((cmd >> 4) & 0x0f) << 4))
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        byte = ((self.backlight << 3) |((cmd & 0x0f) << 4))
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        if cmd <= 3:utime.sleep_ms(5)
        gc.collect()

    def hal_write_data(self, data):
        byte = (0x01 |(self.backlight << 3) |(((data >> 4) & 0x0f) << 4))
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        byte = (0x01 |(self.backlight << 3) |((data & 0x0f) << 4))      
        self.i2c.writeto(self.i2c_addr, bytes([byte | 0x04]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        gc.collect()


if __name__ == '__main__':main()