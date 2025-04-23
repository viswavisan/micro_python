from machine import Pin
import utime

class ultra:
    def __init__(self):
        self.trigger = Pin(14, Pin.OUT)
        self.echo = Pin(15, Pin.IN)
    def trigger_signal(self):
        self.trigger.low()
        utime.sleep_us(2)
        self.trigger.high()
        utime.sleep_us(5)
        self.trigger.low()
    def get_signal(self):
        while self.echo.value() == 0:signaloff = utime.ticks_us()
        while self.echo.value() == 1:signalon = utime.ticks_us()
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        return distance
