from machine import Pin
from time import sleep, sleep_ms

# Motor control pins
in1 = Pin(0, Pin.OUT)
in2 = Pin(1, Pin.OUT)

def stop():
    in1.low()
    in2.low()

def forward():
    in1.high()
    in2.low()

def backward():
    in1.low()
    in2.high()

# Simulated PWM speed control
def run_motor_fake_pwm(direction='forward', speed_percent=100, run_time=3):
    """
    direction: 'forward' or 'backward'
    speed_percent: 0 to 100
    run_time: total duration in seconds
    """
    cycle_time_ms = 20  # total period of one fake PWM cycle
    on_time = int(cycle_time_ms * (speed_percent / 100))
    off_time = cycle_time_ms - on_time

    direction_fn = forward if direction == 'forward' else backward

    loops = int((run_time * 1000) / cycle_time_ms)

    for _ in range(loops):
        if on_time > 0:
            direction_fn()
            sleep_ms(on_time)
        if off_time > 0:
            stop()
            sleep_ms(off_time)

    stop()

# === Test Motor ===

#Run at full speed
print("Full speed...")
run_motor_fake_pwm('forward', 40, 2)


# Run in reverse at 80% speed
print("Reverse at 20%...")
run_motor_fake_pwm('backward', 40, 5)

# Stop
stop()
