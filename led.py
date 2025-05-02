from machine import Pin, PWM, I2C
import time
import utime
import gc
from time import sleep
from micropython import const
import framebuf,neopixel

class PIN:
    '''LED related code #verified
    |------------------------------------------------------|
    |item        | price     | voltage   | description     |
    |------------------------------------------------------|
    |LED-bulb    | ~1 rs     | ~3v       |                 |
    |------------------------------------------------------|
    |RGB =bulb   | ~3 rs     | ~3v       |                 |
    |------------------------------------------------------|
    |LED-strip   | ~1000 rs  | ~5v       | ws2812B         |
    |------------------------------------------------------|

    '''
    def __init__(self,type='led',pin='LED',num_leds=3):
        self.type=type
        if type == 'strip':self.led=neopixel.NeoPixel(Pin(pin), num_leds)
        elif type == 'rgb':
            self.led = [PWM(Pin(p)) for p in pin]
            for p in self.led:p.freq(1000)
        else:self.led=Pin(pin, Pin.OUT)

    def set_color(self,r,g,b,led_number=0):
        if self.type=='strip':
            self.led[led_number] = (r, g, b)
            self.led.write()
        elif self.type=='rgb':
            colors = [-(min(255, c)-255) for c in [r, g, b]]
            for p, c in zip(self.led, colors):p.duty_u16(65535 - int(c * 257))
    def off(self):
        if self.type=='strip':
            for i in range(len(self.led)):self.led[i]=(0,0,0)
            self.led.write()
        elif self.type=='rgb':
            for p in self.led:p.duty_u16(0)
        else:self.led.off()
    def on(self):self.led.on()



class OLED(framebuf.FrameBuffer):
    '''disply module #verified
    |-------------------------------------------------------|
    |item         | price     | voltage   | description     |
    |-------------------------------------------------------|
    |oled with i2c| ~200 rs   | ~3v       |0.96 inch ssd1306|
    |-------------------------------------------------------|
    |oled with i2c| ~150 rs   | ~3v       |0.91 inch ssd1306|
    |-------------------------------------------------------|

    '''
    def __init__(self):
        SET_DISP = const(0xAE)
        SET_MEM_ADDR = const(0x20)
        SET_COL_ADDR = const(0x21)
        SET_PAGE_ADDR = const(0x22)
        SET_CONTRAST = const(0x81)
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


class LcdApi:
    '''disply module #verified
    |-------------------------------------------------------|
    |item         | price     | voltage   | description     |
    |-------------------------------------------------------|
    |16X2 LCD     | ~100 rs   | ~5v       |                 |
    |-------------------------------------------------------|
    |i2c          | ~100 rs   | ~5v       |                 |
    |-------------------------------------------------------|
    '''
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
    print('running')
    led=PIN('led','LED')
    led.on()
    rgb=PIN('rgb',[1,2,3])
    rgb.set_color(255,0,0)
    strip=PIN('strip',4,3)
    strip.set_color(255,0,0,0)
    strip.set_color(1,255,0,1)

    strip.off()
    led.off()
    rgb.off()


