import flask
import json
import time
from mqtt_client import device_interface as Server
from mqtt_client import get_topic_and_payload

server_id = "server"

server = Server(server_id)
app = flask.Flask(__name__)

url_send_back = {}

def generate_url(pic_name,topic,time):
    url = "http://52.184.15.163:5000/get_pic"
    return flask.url_for(url,pic_name=pic_name,topic=topic,time=time)

@app.route("/upload",methods=["GET","POST"])
def upload(pic_name, topic, time):
    uploadfile = flask.request.files.get("pic_name")
    path = "".join(get_pic_path(topic, time))
    if uploadfile:
        uploadfile.save(path)
        url = generate_url(pic_name,topic,time)
        localtime = time.strftime("%Y%m%d%H%M%S", time.localtime())
        payload_to_send = "find_stranger " + localtime +" " + url
        for app_topic in url_send_back[topic]:
            server.publish(app_topic,payload_to_send,2)
        url_send_back[topic] = None
        return 0
    return 1


@app.route("/hello")
def hello():
    return "hello"

@app.route("/lock",methods=["GET","POST"])
def lock():
    for topic in server.topic["2device"]:
        server.publish(topic,"lock",2)
    return "0"
    

@app.route("/unlock",methods=["GET","POST"])
def unlock():
    for topic in server.topic["2device"]:
        server.publish(topic,"unlock",2)
    return "0"

@app.route("/test",methods=["GET","POST"])
def lock_or_unlock():
    json_data = str(flask.request.data,encoding="utf-8")
    # json_data = flask.request.form.get('data')
    # json_data = str(flask.request.data ,encoding="utf-8"))
    json_data = json.loads(json_data)
    action = json_data['name']
    if action is 'lock':
        print("get lock from mssage")
        return lock()
    elif action is 'unlock':
        print("get unlock from mssage")
        return unlock()
    print("get unkown meaage from app")
    return "1"

@app.route("/get_pic",methods=["GET","POST"])
def get_pic(pic_name, topic, time):
    dir_path,filename = get_pic_path(topic, time)

    return flask.send_from_directory(directory= dir_path, filename= filename)

def get_pic_url(topic, time):
    return "http://52.184.15.163:5000/get_pic"


def get_pic_path(topic, time):
    path = "./upload/"
    filename = topic+"pic"+time+".jpg"
    return path,filename



@server.add_action2
def find_stranger(msg, client):
    topic, payload = get_topic_and_payload(msg)
    tmp = payload.split()
    topic_num = int(tmp[1])
    topic = tmp[-2]
    url_send_back[topic] = []
    for i in range(topic_num):
        topic_to_send = tmp[i+2]
        if topic_to_send in client.topic_in_use:
            url_send_back[topic] = topic_to_send

server.add_action(lock)
server.add_action(unlock)
server.add2device_topic("todevice")
server.add2app_device_topic("toapp")

def get_add_device_app_return_msg(msg):
    topic,payload = get_topic_and_payload(msg)
    msgs = payload.split()
    action_name = "hand_shake"
    device_id = msgs[1]
    device_topic = msgs[2]
    app_id = msgs[3]
    app_topic = msgs[4]
    ret_json = {"action_name":action_name,"device_id":device_id,"device_topic":device_topic,\
        "app_id":app_id,"app_topic":app_topic,"state":0}
    # ret_json = json.dumps(ret_json)
    ret_topic = app_topic if msgs[0] == "add_app" else device_topic
    return ret_topic,ret_json

@server.add_action2
def add_device(msg):
    """
        从device发来的设备添加信息
    """
    topic,payload = get_add_device_app_return_msg(msg)
    payload = "hand_shake "+payload["app_id"]+" "+payload["device_id"]+" "+payload["state"]
    server.publish(topic,payload,2)


@server.add_action2
def add_app(msg):
    """
        从app发来的设备添加信息
    """
    topic,payload = get_add_device_app_return_msg(msg)
    payload = json.dumps(payload)
    server.publish(topic,payload,2)

def add_rusult():
    pass

if __name__ == "__main__":
    host = "52.184.15.163"
    flask_host = "10.0.2.4"
    flask_port = 5000
    port = 1883
    server.run("345", host, port)
    server.add_subscribe(server.topic["2server"])
    app.run(flask_host,flask_port)
    loop_time = 1
    while True:
        print("loop time is ",loop_time)
        time.sleep(10)