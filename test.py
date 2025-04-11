from machine import Pin
import time

sensor = Pin(15, Pin.IN)  # Use your actual GPIO pin
sensor.value(0)
while True:
    print("Light detected" if sensor.value() == 1 else "Dark")
    time.sleep(0.5)
    sensor.value(0)