from machine import Pin, PWM
import time

in1 = Pin(0, Pin.OUT)
in2 = Pin(1, Pin.OUT)
ena = PWM(Pin(2))
ena.freq(1000)
min_duty = 0
max_duty = 45535

def backward(speed_percent):
    in1.low()
    in2.high()
    duty = int(min_duty + (max_duty - min_duty) * (speed_percent / 100))
    ena.duty_u16(duty)


def stop():
    in1.low()
    in2.low()
    ena.duty_u16(0)
try:

        backward(80)
        time.sleep(5)
        stop()

except KeyboardInterrupt:
    print("\nInterrupted! Stopping motor.")
    stop()
