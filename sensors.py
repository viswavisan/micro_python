from machine import Pin
import utime
trigger = Pin(14, Pin.OUT)
echo = Pin(15, Pin.IN)
def ultra():
   try:
        trigger.low()
        utime.sleep_us(2)
        trigger.high()
        utime.sleep_us(5)
        trigger.low()
        while echo.value() == 0:
            signaloff = utime.ticks_us()
            if signaloff>132136867*10:print(signaloff)
        while echo.value() == 1:
            signalon = utime.ticks_us()
            if signalon>132136867*10:print(signalon)
        timepassed = signalon - signaloff
        distance = (timepassed * 0.0343) / 2
        if distance <30: print('abstrucle found', distance)
        # print("The distance from object is ",distance,"cm")
   except:return
while True:
   ultra()
   utime.sleep(1)