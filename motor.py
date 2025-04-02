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

class DC_motor:
    def __init__(self, pin):pass
    # Pin Definitions
    MOTOR_PIN1 = 15  # GPIO15 for Motor Control (IN1)
    MOTOR_PIN2 = 14  # GPIO14 for Motor Control (IN2)

    # Motor Pins Setup
    motor1 = Pin(MOTOR_PIN1, Pin.OUT)
    motor2 = Pin(MOTOR_PIN2, Pin.OUT)

    # Function to control motor direction and speed
    def control_motor(self,direction, speed):
        pwm = PWM(self.motor1 if direction == "forward" else self.motor2)
        pwm.freq(1000)  # 1 kHz frequency
        pwm.duty_u16(int(speed * 65535 / 100))  # Convert speed to 16-bit value
        time.sleep(2)
        pwm.deinit()
        self.motor1.off()
        self.motor2.off()


class AC_motor:
    RELAY_PIN = 15  # GPIO15 to control the relay

    # Setup
    relay = Pin(RELAY_PIN, Pin.OUT)

    # Function to control AC Motor
    def control_motor(state):
        if state == "on":
            relay.on()  # Activates relay, motor ON
            print("Motor ON")
        elif state == "off":
            relay.off()  # Deactivates relay, motor OFF
            print("Motor OFF")


class stepper_motor:
    # Pin Definitions
    IN1 = Pin(15, Pin.OUT)
    IN2 = Pin(14, Pin.OUT)
    IN3 = Pin(13, Pin.OUT)
    IN4 = Pin(12, Pin.OUT)

    # Step sequence for a 28BYJ-48 stepper motor
    step_sequence = [
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 1, 0],
        [0, 0, 1, 1],
        [0, 0, 0, 1],
        [1, 0, 0, 1],
    ]

    # Function to control stepper motor
    def stepper_move(self,steps, delay):
        for _ in range(steps):
            for step in self.step_sequence:
                self.IN1.value(step[0])
                self.IN2.value(step[1])
                self.IN3.value(step[2])
                self.IN4.value(step[3])
                time.sleep(delay)

