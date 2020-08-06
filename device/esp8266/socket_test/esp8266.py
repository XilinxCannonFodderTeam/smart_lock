import network
import socket
import ujson
import utime
from simple import MQTTClient

def connect(ssid, password, wlan = network.WLAN(network.STA_IF)):
    wlan.active(True)
    if not wlan.isconnected():
        print("connecting to network...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            return False
    return True


device_id = "device"
device_topic = "todevice"
device_info = {"device_id":device_id,"device_topic":device_topic}
send_data = "HTTP/1.1 200 OK\r\nConnection:close\r\n\r\n" + ujson.dumps(device_info)
ip_config = ("192.168.0.2","255.255.255.0","192.168.0.1","8.8.8.8")
ssid_ap = "ESP_lock"
password_ap = "12345678"
port = 8989
ssid = "Redmi K30 Pro Zoom Ed..._1oN3​"
password = "sl172919"
wlan = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)
broker = "52.184.15.163"
mqtt_id = "esp_lock"
mqtt_port = 1883
keepalive = 60
mqtt_client = None
localtime = "20200731110320"
finish = False
app_id = "app"
app_topic = "toapp"


def recv_all_by_timeout(client_socket):
    data = ""
    while True:
        try:
            data_tmp = client_socket.recv(1024)
            if len(data_tmp) == 0:
                break
            data += str(data_tmp)
            print(str(data_tmp))
        except OSError:
            break
    return data

def check_magic_num(paras):
    if "magic_number" in paras.keys():
        if int(paras["magic_number"]) == 123:
            return True
    return False

def listen_socket(addr):
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    s = socket.socket()
    s.bind(addr)
    s.listen(2)
    paras = None
    print("dowm listen 2 connect")
    while True:
        print("start to accept connection")
        c,addr = s.accept()
        c.settimeout(0.5)
        print("addr is ",addr)
        data = recv_all_by_timeout(c)
        print("recv all data")
        paras = parse_url_parameter(data)
        if check_magic_num(paras):
            c.send(send_data)
            c.close()
            break
        c.close()
    return paras


def parse_url_parameter(get_msg):
    msg = str(get_msg)
    msgs = msg.split()
    method = msgs[0][2:]
    ret = None
    if method == "GET":
        print("GET method**************")
        get_url = msgs[1]
        get_url = get_url[2:]
        paras = get_url.split("&")
        ret = {}
        for para in paras:
            tmp = para.find("=")
            key = para[:tmp]
            value = para[tmp+1:]
            ret[key] = value
    elif method == "POST":
        print("POST method*********")
        body = msg.split("\\r\\n\\r\\n")[-1]
        if body.startswith('\''):
            body = body[3:-1]
        print("body:",body)
        ret = ujson.loads(body)
        print("ret:",ret)
        print("ret_type",type(ret))
        for key in ret:
            print(key,ret[key])
    return ret

def create_ap_station(ssid, password, ap = network.WLAN(network.AP_IF)):
    ap.active(True)
    ap.config(essid=ssid, authmode = network.AUTH_WPA_WPA2_PSK, password=password)
    ap.ifconfig(ip_config)

def send_msg_to_server(topic,app_id,app_topic,device_id,device_topic,time):
    mqtt_client = MQTTClient(mqtt_id,broker,mqtt_port,keepalive=keepalive)
    payload = "add_device "+device_id+" "+device_topic+" "+app_id+" "+app_topic+" "+time
    mqtt_client.set_callback(on_message)
    mqtt_client.connect()
    mqtt_client.subscribe(device_topic,qos=2)
    mqtt_client.publish(topic,payload,qos=0)
    
def on_message(topic,msg):
    print(msg)
    msg = str(msg)
    msgs = msg.split()
    if msgs[-1] == "0":
        finish = True
        print("finish the device find process")
    elif msgs[-1] == "1":
        finish = False
        print("fail to add app manager")
    else:
        print("unkown error code")

FOR_TEST = False

def main():

    while True:
        finish = False
        print("open the ap with name",ssid_ap,"and passwod ",password_ap)
        create_ap_station(ssid_ap, password_ap, ap)
        utime.sleep(0.5)
        localip = ap.ifconfig()[0]
        addr = (localip,port)
        print("waiting for connect tcp socket in addr",addr)
        paras = listen_socket(addr)
        ssid = paras["wifi"]
        password = paras["password"]
        app_id = paras["app_id"]
        app_topic = paras["app_topic"]
        print("get the info:",paras)
        connect(ssid,password,wlan)
        utime.sleep(0.5)
        if wlan.isconnected():
            print("success to connect ap",ssid)
            send_msg_to_server("toserver",app_id,app_topic,device_id,device_topic,localtime)
        for i in range(10):
            utime.sleep(0.2)
            if finish:
                break
        if finish:
            break
    print("finish and end the loop")
    while True:
        utime.sleep(1)


#main()
