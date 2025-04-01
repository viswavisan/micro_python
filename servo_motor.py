from machine import Pin, PWM
import time

class servo_sg90:
    def __init__(self):
        self.servo = PWM(Pin(15))
        self.servo.freq(50)
        self.current_angle = 0
        self.set_angle(self.current_angle)
    def set_angle(self,angle):
        self.servo.duty_u16(int(1495+((8153-1495)*angle/180)))

    def move_to_angle(self,target_angle, delay=0.02):
        try:
            
            if self.current_angle < target_angle:inc=1
            else: inc=-1
                
            while True:
                self.current_angle+=inc
                if (target_angle-(self.current_angle)*inc)<=0:break
                self.set_angle(self.current_angle)
                time.sleep(delay)
        except Exception as e:print(str(e))

try:
    servo=servo_sg90()

    while True:
        servo.move_to_angle(0)
        servo.move_to_angle(180)
        servo.move_to_angle(0)
except Exception as e:print(str(e))