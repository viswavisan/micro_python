from machine import Pin, PWM
import time

class PIN:
    def __init__(self):pass
    def RGB(self,r_pin,g_pin,b_pin,r=255,g=255,b=255):
        colors = [min(255, c) for c in [r, g, b]]
        pwm_channels = [PWM(Pin(p)) for p in [r_pin,g_pin,b_pin]]
        for p in pwm_channels:p.freq(1000)
        for p, c in zip(pwm_channels, colors):p.duty_u16(65535 - int(c * 257))
    def STATE(self,pin):return Pin(pin, Pin.OUT)