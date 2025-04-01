
import time,utime
from machine import Pin,PWM,Timer,I2C
from array import array
from utime import ticks_us, ticks_diff
from micropython import const
import framebuf

#LED


class PIN:
    def __init__(self):pass
    def RGB(self,r_pin,g_pin,b_pin,r=255,g=255,b=255):
        colors = [min(255, c) for c in [r, g, b]]
        pwm_channels = [PWM(Pin(p)) for p in [r_pin,g_pin,b_pin]]
        for p in pwm_channels:p.freq(1000)
        for p, c in zip(pwm_channels, colors):p.duty_u16(65535 - int(c * 257))
    def STATE(self,pin):return Pin(pin, Pin.OUT)

    

class temperature:
    def __init__(self):
        pass
    def onboard_temperature(self):
        return 27 - (machine.ADC(4).read_u16() * (3.3 / 65535.0)- 0.706) / 0.001721

class servo_sg90:
    def __init__(self):
        self.servo = PWM(Pin(28))
        self.servo.freq(50)
        self.current_angle = 0
    def set_angle(self,angle):
        self.servo.duty_u16(int(1495+((8153-1495)*angle/180)))

    def move_to_angle(self,target_angle, delay=0.02):
        try:
            self.set_angle(self.current_angle)
            if self.current_angle < target_angle:inc=1
            else: inc=-1
                
            while True:
                self.current_angle+=inc
                if (target_angle-(self.current_angle)*inc)<=0:break
                self.set_angle(self.current_angle)
                time.sleep(delay)
        except Exception as e:print(str(e))

class IR_RX:

    def __init__(self):
        self._pin = Pin(11, Pin.IN)
        # self._nedges = 28
        # self._tblock = 30
        self._nedges = 68
        self._tblock = 80
        self._errf = lambda _ : None
        self.verbose = False

        self._times = array('i',  (0 for _ in range(self._nedges + 1))) 
        self._pin.irq(handler = self._cb_pin, trigger = (Pin.IRQ_FALLING | Pin.IRQ_RISING))
        self.edge = 0
        self.tim = Timer(-1)
        self.cb = self.decode

    def _cb_pin(self, line):
        t = ticks_us()
        if self.edge <= self._nedges:
            if not self.edge: self.tim.init(period=self._tblock , mode=Timer.ONE_SHOT, callback=self.cb)
            self._times[self.edge] = t
            self.edge += 1

    def close(self):
        self._pin.irq(handler = None)
        self.tim.deinit()

    def decode(self, _,protocol='nec'):
        try:
            if not 14 <= self.edge <= 68:raise RuntimeError('edge out of range')
            if protocol=='nec':
                width = ticks_diff(self._times[1], self._times[0])
                width = ticks_diff(self._times[2], self._times[1])
                if 3000 > width > 4000:raise RuntimeError('width not in range')
                val = sum(((ticks_diff(self._times[edge + 1], self._times[edge]) > 1120) << (31 - i)) for i, edge in enumerate(range(3, 68 - 2, 2)))

                cmd, addr = val & 0xff, (val >> 16) & 0xff
                if addr != (val >> 24) ^ 0xff or cmd != ((val >> 8) ^ 0xff) & 0xff: raise RuntimeError('invalid address')
                self.edge = 0
     
            else:
                bits,bit,v,x = 1,1,1,0
                while bits < 14:
                    if x > self.edge - 2:raise RuntimeError('short signals exceeded')
                    width = ticks_diff(self._times[x + 1], self._times[x])
                    if not 500 < width < 3500:raise RuntimeError('width not in range')
                    bit,v,bits, x  = (bit ^ 1) if width >= 1334 else bit, (v << 1) | bit,bits + 1, x + 1 + (width < 1334)

                addr, cmd = (v >> 6) & 0x1f, (v >> 11) & 1
                self.edge = 0

        except RuntimeError as e:self.edge = 0;print(str(e))

        if cmd==186:PIN().STATE(16).on()
        if cmd==233:PIN().STATE(16).off()

class OLED(framebuf.FrameBuffer):
    def __init__(self):
        DISPLAY_OFF = const(0xAE) | 0x00
        DISPLAY_ON = const(0xAE)| 0x01
        SET_MEM_ADDR = const(0x20)
        INVERT_DISPLAY = const(0xA7) #text color black
        NORMAL_DISPLAY = const(0xA6) #text color white | default


        self.i2c=I2C(1, scl=Pin(27), sda=Pin(26), freq=200000)
        width,height,self.addr=128,64,0x3C
        self.buffer = bytearray((height // 8) * width)
        super().__init__(self.buffer, width, height, framebuf.MONO_VLSB)
        cmds = [ DISPLAY_OFF,SET_MEM_ADDR, 0x00, DISPLAY_ON]
        for cmd in cmds:self.i2c.writeto(self.addr, bytearray([0x80, cmd]))
        self.clear()
       
    def show(self):
        self.i2c.writeto(self.addr, bytearray([0x40]) + self.buffer)
    
    def clear(self):
        self.fill(0)
        self.show()


class sound:
    def __init__(self,pin):
        self.buzzer = PWM(Pin(pin))
        self.buzzer.freq(1000) 

    def start(self,notes = [262],duration = 0.3):
        for note in notes:
            self.buzzer.freq(note)
            self.buzzer.duty_u16(32768)
            time.sleep(duration)
            self.buzzer.duty_u16(0)
            time.sleep(0.1)

ir=IR_RX()
PIN().STATE('LED').on()
PIN().STATE(12).on()
PIN().RGB(13,14,15,250,0,250)

sound(21).start([262, 294, 330, 349, 392, 440, 494, 523])

servo=servo_sg90()
servo.move_to_angle(180)
servo.move_to_angle(0)



oled = OLED()
fb = framebuf.FrameBuffer(bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00|?\x00\x01\x86@\x80\x01\x01\x80\x80\x01\x11\x88\x80\x01\x05\xa0\x80\x00\x83\xc1\x00\x00C\xe3\x00\x00~\xfc\x00\x00L'\x00\x00\x9c\x11\x00\x00\xbf\xfd\x00\x00\xe1\x87\x00\x01\xc1\x83\x80\x02A\x82@\x02A\x82@\x02\xc1\xc2@\x02\xf6>\xc0\x01\xfc=\x80\x01\x18\x18\x80\x01\x88\x10\x80\x00\x8c!\x00\x00\x87\xf1\x00\x00\x7f\xf6\x00\x008\x1c\x00\x00\x0c \x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"), 32, 32, framebuf.MONO_HLSB)
oled.blit(fb, 96, 0)
oled.text("Temperature", 5, 5)
oled.text(str(temperature().onboard_temperature()), 5, 15)
oled.show()


try:
    while True:pass
except KeyboardInterrupt:ir.close()
