#LCD 16x2
import utime
import gc
from machine import I2C, Pin
from time import sleep

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

if __name__ == '__main__':
    lcd=LcdApi()
    lcd.write('keerthana')
    sleep(5)