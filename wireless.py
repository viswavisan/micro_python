import network
import time,database

from machine import Timer, Pin,PWM
from array import array
from utime import ticks_us, ticks_diff
from time import sleep_us

wlan = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)

class wifi:
    def __init__(self):
        pass
    def enable_hotspot(self):
        ap.active(False)
        time.sleep(2)
        ap.config(essid='picow', password='picow123')
        ap.active(True)
        while not ap.active():time.sleep(1)
        return {'status':'success','message':f'hotspot enabled:{ap.ifconfig()[0]}'}

    def check_status(self):
        if wlan.isconnected():
            return {'status':'success','message':f'Connected with {wlan.config('essid')} ({wlan.ifconfig()[0]})'}
        else: return {'status':'failure','message':'Not connected'}

    def connect_wifi(self,ssid='Devil', password='annyeo12'):
        try:
            print('trying to connect wifi') 
            wlan.active(False)
            time.sleep(1)
            wlan.active(True)
            wlan.connect(ssid, password)
            for _ in range(10):
                status=self.check_status()
                if status['status']=='success':
                    database.table['wifi'][ssid]=password
                    with open('database.py', 'w') as f:f.write(f'table={str(database.table)}')
                    return status
                print('reconnecting')
                time.sleep(1)
            return status
        except Exception as e: return {'status':'error','message':str(e)}
    
    def auto_connect(self):
        print('trying auto connect')
        try:
            wlan.active(False)
            time.sleep(1)
            wlan.active(True)
            for network_info in wlan.scan():
                ssid=network_info[0].decode()
                if ssid in database.table['wifi']:
                    x=self.connect_wifi(ssid,database.table['wifi'][ssid])
                    return x

        except Exception as e:return str(e)


class IR_RX():

    def __init__(self):
        self._pin = Pin(11, Pin.IN)
        self._nedges = 68
        self._tblock = 80
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
                if not 14 <= self.edge <= 68:raise RuntimeError('Edge out of range')
                pulse_duration=[ticks_diff(self._times[i], self._times[i - 1]) for i in range(1, self.edge)]     
                width = ticks_diff(self._times[1], self._times[0])
                if 3000 > width > 4000:raise RuntimeError('Width not in range')
                val = sum(((ticks_diff(self._times[edge + 1], self._times[edge]) > 1120) << (31 - i)) for i, edge in enumerate(range(3, 68 - 2, 2)))
                cmd, addr = val & 0xff, (val >> 16) & 0xff
                if addr != (val >> 24) ^ 0xff or cmd != ((val >> 8) ^ 0xff) & 0xff:raise RuntimeError('Invalid address')
                print(f"NEC: Addr={addr}, Cmd={cmd}")
                print(pulse_duration)
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
                print(addr, cmd)
        

        except RuntimeError as e:self.edge = 0;print(str(e))
    
class IR_TX:

    def __init__(self):
        self.pwm = PWM(Pin(15, Pin.OUT))
        self.pwm.freq(38000)
        self.pwm.duty_u16(0)

    def send_pulse(self,duration_us, is_high):
        self.pwm.duty_u16(32768 if is_high else 0)
        sleep_us(duration_us)
        self.pwm.duty_u16(0)

    def send_signal(self,signal):
        for pulse in signal:
            self.send_pulse(pulse, is_high=True)
            sleep_us(100)
            self.send_pulse(0, is_high=False)
            sleep_us(100)
        self.pwm.deinit()

# ir=IR_RX()
# signal = [8996, 4500, 526, 528, 526, 526, 526, 527, 526, 533, 522, 531, 521, 532, 521, 535, 517, 528, 525, 1688, 527, 1689, 525, 1687, 526, 1688, 527, 1687, 527, 1687, 527, 1689, 524, 1688, 528, 525, 532, 1684, 525, 527, 526, 526, 527, 526, 528, 1686, 527, 528, 524, 1688, 528, 1686, 527, 528, 525, 1687, 536, 1678, 527, 1687, 527, 526, 529, 1686, 526, 528, 525]
# irt=IR_TX()
# irt.send_signal(signal)

# import bluetooth


# class BT:
#     MOTOR_PIN = 15
#     motor = Pin(MOTOR_PIN, Pin.OUT)
#     bt = bluetooth.BLE()
#     bt.active(True)
#     bt.gap_advertise(100, b'\x02\x01\x06\x03\x03\x12\x18')

#     def __init__(self, pin):pass


#     # Function to handle incoming commands
#     def bt_callback(self,event, data):
#         if event == 1:  # Event 1 is typically data received
#             command = data.decode().strip()
#             self.control_motor(command)

#     # Function to control motor
#     def control_motor(self,command):
#         if command == 'forward':
#             self.motor.on()
#             print("Motor Moving Forward")
#         elif command == 'backward':
#             self.motor.off()
#             print("Motor Stopped")

class RF:
    TX_PIN = 15
    RX_PIN = 14
    transmitter = Pin(TX_PIN, Pin.OUT)
    receiver = Pin(RX_PIN, Pin.IN)
    def __init__(self):pass

    def send_signal(self,command):
        for _ in range(5):  # Send command 5 times for reliability
            if command == "forward":
                self.transmitter.on()
                time.sleep(0.001)
                self.transmitter.off()
                time.sleep(0.001)
            elif command == "backward":
                self.transmitter.on()
                time.sleep(0.002)
                self.transmitter.off()
                time.sleep(0.001)

    def receive_signal(self):
        received = []
        start_time = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), start_time) < 1000:
            if self.receiver.value() == 1:
                received.append(1)
                time.sleep(0.001)
            else:
                received.append(0)
                time.sleep(0.001)
        return "forward" if received.count(1) > 20 else "backward"
