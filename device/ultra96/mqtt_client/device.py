from mqtt_client import _load_python_file,_save_input_py_file,get_topic_and_payload
from mqtt_client import device_interface as Client
from led import led_off,led_on
from face_api import detect
import time
import requests
import cv2



def print_msg(msg, client):
    topic,payload = get_topic_and_payload(msg)
    print(topic)
    print(payload)

def find_stranger(topics):
    if isinstance(topics, str):
        payload = "find_stranger 1 "+ topics + " "
    else: 
        payload = "find_stranger " + str(len(topics)) +" " + " ".join(topics) + " "
    localtime = time.strftime("%Y%m%d%H%M%S", time.localtime())
    payload = payload + localtime
    # print(payload)
    client.publish(client.topic["2server"], payload, client.qos)
    
def upload_pic(frame):
    url = "http://52.184.15.163:5000/upload"
    params_data = {"pic_name":"test.jpg","topic":"device_id","time":"202007291709"}
    files = {'file':(frame)}
    r = requests.post(url, params=params_data, files=files)
    print("get state code is :",r.status_code)





device_id = "device"
device_topic_sub = "todevice"
app_topic = "toapp"
app_id = "app"
host = "52.184.15.163"
port = 1883
client = Client(device_id)
client.run("123", host, port)
time.sleep(1)
client.add_subscribe(device_topic_sub)
client.add_action(_load_python_file)
client.add_action(_save_input_py_file)
client.add2device_topic("todevice")
client.add2app_device_topic("toapp")

@client.add_action2
def starnger_test():
    print("this is test for find stranger")
    find_stranger("toapp")
    print("finish to send msg 1")
    img = cv2.imread("./test.jpg")
    upload_pic(img)
    print("finish to send msg 3")

@client.add_action2
def lock():
    print("hello from lock")
    led_on()
    payload = "lock_response 0 "+device_id+" "+app_id
    client.publish(app_topic,payload,2)

@client.add_action2
def unlock():
    print("hello from unlock")
    led_off()
    payload = "unlock_response 0 "+device_id+" "+app_id
    client.publish(app_topic,payload,2)




if __name__ == "__main__":
    loop_time = 1
    while True:
        img,face_id = detect(0)
        if not face_id:
            find_stranger("toapp")
            upload_pic(img)
