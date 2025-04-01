print('starting')
import gc
gc.mem_free()
import connection
from miniserver import Server
import os
import machine

x=connection.enable_hotspot()
print(x)


return_value={}

led = machine.Pin("LED", machine.Pin.OUT)
led.off()
led.on()

app = Server()

@app.get("/")
def home(data=None):
    temp=27 - (machine.ADC(4).read_u16() * (3.3 / 65535.0)- 0.706) / 0.001721
    memory=f'{264-(gc.mem_free()// 1024)} KB/264 KB'
    context = {'temperature':temp,'memory':memory}
    return app.template_response('index.html', context)

@app.post("/execute")
def execute(request:dict=None):
    try:
        return_value.clear()
        if 'cmd' in request:exec(request['cmd']);return return_value
        return 'working fine'
    except Exception as e:return str(e)

@app.get("/script.js")
def serve_js(data: dict = None):    
    with open('script.js', 'rb') as f:content = f.read()
    return content.decode('utf-8')

@app.get("/style.css")
def serve_js(data: dict = None):    
    with open('style.css', 'rb') as f:content = f.read()
    return content.decode('utf-8')

app.run()