from machine import Pin, PWM
import time

#servo motor 180 deg rotation
class servo_sg90:
    def __init__(self):
        self.servo = PWM(Pin(15))
        self.servo.freq(50)
        self.current_angle = 0
        self.set_angle(self.current_angle)
    
    def set_angle(self,angle):self.servo.duty_u16(int(1495+((8153-1495)*angle/180)))

    def move_to_angle(self,target_angle, delay=0.02):
        try:  
            inc = 1 if self.current_angle < target_angle else -1    
            while True:
                self.current_angle+=inc
                if (target_angle-(self.current_angle)*inc)<=0:break
                self.set_angle(self.current_angle)
                time.sleep(delay)
        except Exception as e:print(str(e))

class DC_motor:
    # with H-bridge
    def __init__(self):
        self.m1f = Pin(0, Pin.OUT)
        self.m1b = Pin(1, Pin.OUT)
        self.m1s = PWM(Pin(2))
        self.m1s.freq(1000)
        self.min_duty = 25000
        self.max_duty = 45535


    def run(self,direction='forward',speed_percent=None):
        time.sleep(0.5)
        if direction=='forward':self.m1f.low();self.m1b.high()
        elif direction=='backward':self.m1f.high();self.m1b.low()
        else:self.m1f.low();self.m1b.low();self.m1s.duty_u16(0)
        if speed_percent:self.speed(speed_percent)

    def speed(self,speed_percent):
        duty = int(self.min_duty + (self.max_duty - self.min_duty) * (speed_percent / 100))
        self.m1s.duty_u16(duty)

    def stop(self):
        self.m1f.low()
        self.m1b.low()
        self.m1s.duty_u16(0)

#single speed single direction
class AC_motor:
    def __init__(self):
        self.relay = Pin(15, Pin.OUT)

    def control_motor(self,state):
        if state == "on":self.relay.on()
        elif state == "off":self.relay.off()

class stepper_motor:
    #with A4988 driver
    def __init__(self):
        self.dir_pin = Pin(2, Pin.OUT)
        self.step_pin = Pin(3, Pin.OUT)

    def step_motor(self,steps, delay_ms, direction):
        self.dir_pin.value(direction)
        for _ in range(steps):
            self.step_pin.value(1)
            self.step_pin.value(0)
            time.sleep_ms(delay_ms)
try:
    m=DC_motor()
    m.speed(10)
    m.run('forward')
    time.sleep(5)
    m.run('backward')
    time.sleep(3)
    m.stop()
except:
    m.stop()