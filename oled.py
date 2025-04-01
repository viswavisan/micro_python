from micropython import const
from machine import Pin, I2C
import framebuf

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

if __name__ == '__main__':main()