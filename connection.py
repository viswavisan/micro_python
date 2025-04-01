import network
import time,database

wlan = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)

def enable_hotspot():
    ap.active(False)
    time.sleep(2)
    ap.config(essid='picow', password='picow123')
    ap.active(True)
    while not ap.active():time.sleep(1)
    return {'status':'success','message':f'hotspot enabled:{ap.ifconfig()[0]}'}

def check_status():
    if wlan.isconnected():
        return {'status':'success','message':f'Connected with {wlan.config('essid')} ({wlan.ifconfig()[0]})'}
    else: return {'status':'failure','message':'Not connected'}

def connect_wifi(ssid='Devil', password='annyeo12'):
    try:
        print('trying to connect wifi') 
        wlan.active(False)
        time.sleep(1)
        wlan.active(True)
        wlan.connect(ssid, password)
        for _ in range(10):
            status=check_status()
            if status['status']=='success':
                database.table['wifi'][ssid]=password
                with open('database.py', 'w') as f:f.write(f'table={str(database.table)}')
                return status
            print('reconnecting')
            time.sleep(1)
        return status
    except Exception as e: return {'status':'error','message':str(e)}
    
def auto_connect():
    print('trying auto connect')
    try:
        wlan.active(False)
        time.sleep(1)
        wlan.active(True)
        for network_info in wlan.scan():
            ssid=network_info[0].decode()
            if ssid in database.table['wifi']:
                x=connect_wifi(ssid,database.table['wifi'][ssid])
                print(x)
                return x

    except Exception as e:return str(e)

auto_connect()