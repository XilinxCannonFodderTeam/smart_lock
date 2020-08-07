import paho.mqtt.client as mqtt
import os
import json
import copy
import importlib
import datetime
import time
import threading
import logging
import threading


# 单例模式的开启标识，如果为真，则启用单例模式 | The open flag of singleton mode, if it is true, singleton mode is enabled
# 用于自动导入时函数自动引用 | Used to automatically reference functions during automatic import
ON_SINGLE_PATTERN = False

def _save_input_py_file(msg):
    payload = str(msg.payload, encoding="utf-8")
    first_space = payload.find(' ')
    if first_space < 0:
        return                                 #说明问题的调用，开头应该是函数的别名 | The call to explain the problem should be the alias of the function at the beginning
    path_and_context = payload[first_space+1:] #返回的是第一个空格的位置，所以不要空格所以+1 | Return the first position os <SPACE>, so add 1
    second_space = path_and_context.find(' ')
    if second_space < 0:                       #说明格式不正确 | Indicate format is not valid
        return
    path = path_and_context[:second_space]     #空格不要 | No <SPACE>
    file_context = path_and_context[second_space+1:]
    relpath = os.path.relpath(path)
    if relpath.startswith(".."):               #说明路径不再当前目录下 | Indicate the directory
        return 
    with open(relpath,"w") as f:               #此处不检查文件格式 | Here we do not examine the format of file
        f.write(file_context)

def _load_python_file(msg, client):
    payload = str(msg.payload, encoding="utf-8")
    first_space = payload.find(' ')
    if first_space < 0:
        return                                 #说明问题的调用，开头应该是函数的别名 | Indicate the call of question, so the head shold be the Alias of funcion
    file_paths = payload[first_space+1:]       #返回的是第一个空格的位置，所以不要空格所以+1 | Return the first position os <SPACE>, so add 1
    client.load_python_module(file_paths)


def get_topic_and_payload(msg):
    if not msg:
        return
    topic = msg.topic
    payload = str(msg.payload, encoding="utf-8")
    return topic,payload




class device_interface(mqtt.Client):
    """
        mqtt.Client的继承接口 |  The Inherit Interface of mqtt.Client

        订阅消息，使用subscribe(topic,qos)接口 | Subscrible Message, Use subscribe(topic, qos) Interface

        发布消息，使用publish(topic,payload,qos)接口 | Publish Message, Use publich(topic, payload, qos) Interface

        连接服务器使用run(device_type,host,port)接口 | Connect Sever, Use run(device_type, host, port) Interface

        topic：主题，主题可以订阅也可以发布，对于发布，所有订阅改主题的客户端均会收到发布的消息 | topic: Topic can be subscribed or published. 
                                                                                         For publishing, all clients that subscribe to the topic will receive the published message
        payload：发布的消息，为字符串，推荐长度不超过700字节 | payload: Message published, a string, recommend length less than 700 Byte
        qos：连接的质量等级，0为最低，2为最高，由于设备性能足够，所以2是可以接受的 | qos: Level of Quality, 0 ~ 2, because of the device with enough performance, so 2 is available
        host：连接的broker主机 | The connective Broker Host
        port：连接的broker主机mqtt端口 | The MQTT port of connective Broker Host
        device_type：定义的设备类型，暂时无用 | Defined type of Device ( NOT Used )
    """

    __instance_lock = threading.Lock()

    def __new__(cls, *args, **kargs):
        if ON_SINGLE_PATTERN:
            if not hasattr(device_interface, "_instance"):
                with device_interface.__instance_lock:
                    if not hasattr(device_interface, "_instance"):
                        device_interface._instance =object.__new__(cls)
            return device_interface._instance
        else:
            return object.__new__(cls)

    def __init__(self, client_id="test1", clean_session=None, 
            userdata=None,protocol=4, transport="tcp"):
        """
            client_id：客户端的id号，推荐以'device名称/MAC地址'格式命名 | client_id: ID of Client，recommended name is " 'the name of device'/'MAC Address' "
        """
        super(device_interface,self).__init__(
            client_id=client_id, clean_session=clean_session, 
            userdata=userdata,protocol=protocol, transport=transport
        )
        self.client_id = client_id
        self.__config_file_path = "./config.json"
        self.action = {}
        self.action_load = {}
        self.action_func_name = {}
        self.client = None
        self.host = ""
        self.port = 1883
        self.keepalive = 60
        self.topic_in_use = set()
        self.topic = {"2server":"toserver","2device":set(),"2app_deivce":set()}
        self.device_pair_app2device = {}
        self.device_pair_device2app = {}
        self._rc_mean = ["connect success","wrong proticol",
                "unlegal client id","server can not use","unauthorized"]
        self.use_quick_search = False
        self.qos = 0
        self.__on_running = False
        self.__on_connect = False
        self.default_func = None
        self.default_func_path = None
        self.device_type = ""
        self.__topic_subscribe = []
        


    def load_python_module(self, paths):
        file_paths = paths.split()
        for path in file_paths:
            relpath = os.path.relpath(path)
            if not relpath.startswith('..'):
                tmp = relpath.split(os.sep)           #文件路径的分隔符 | the delimiter of file path
                package = tmp[0][:-3]
                relpath = "." + "/".join(tmp[1:])  #懒得去修改了，反正python自动转义
                module = importlib.import_module(relpath, package)
                print("load module:"+str(module))
                return module

    def __get_func_by_path(self,func_name,func_abs_path):
        """
            此函数的功能是依据函数名称和函数所在文件的绝对路径， | To implement the export function 
            实现函数的导入功能 | according to the function's name and absoulute directory of  file
            原理是使用了python的importlib | Used python.importlib
        """
        path = os.path.relpath(func_abs_path)
        path = path[:-3]
        package = None
        tmp = path.split("\\")
        package = tmp[0]
        path = "." + "/".join(tmp[1:])
        module = importlib.import_module(path, package)
        if func_name in dir(module):
            return getattr(module,func_name)

    def __set_action_by_action_load(self):
        """
            此函数是将所有的self.action_load记录的函数名，函数所在文件对进行导入 | Import all the name and file of functions recorded by self.action_load
        """
        for action in self.action_load.keys():
            func = self.__get_func_by_path(action, self.action_load[action])
            self.add_action(func, self.action_func_name[action])


    def load_from_config(self, config_file_path = None):
        """
            此函数需要与提供的save_to_config一起使用 | NEED save_to_config Function
            config_file_path：的默认位置是同级目录下的config.json | config_file_path: Default location is the config.json in the same directory
            return：返回0表示成功的从配置文件导入,否则为失败 | return: Return 0 to indicate successful import from the configuration file, otherwise it fails
        """
        config_file_path = config_file_path if config_file_path else self.__config_file_path
        if not os.path.isfile(config_file_path):
            return -1
        if self.__on_running:
            self.loop_stop()
        with open(config_file_path,"r") as f:
            info = f.read()
        info_to_save = json.loads(info)
        self.client_id = info_to_save["client_id"]
        self.action_load = info_to_save["action_load"]
        self.action_func_name = info_to_save["action_func_name"]
        self.host = info_to_save["host"]
        self.port = info_to_save["port"]
        self.keepalive = info_to_save["keepalive"]
        self.topic = info_to_save["topic"]
        self.topic["2device"] = set(self.topic["2device"])
        self.topic["2app_deivce"] = set(self.topic["2app_deivce"])
        self.topic_in_use.clear()
        for key in self.topic.keys():
            for topic in self.topic[key]:
                self.topic_in_use.add(topic)
        self.device_pair_app2device = info_to_save["device_pair_app2device"]
        self.device_pair_device2app = info_to_save["device_pair_device2app"]
        self.use_quick_search = info_to_save["use_quick_search"]
        self.qos = info_to_save["qos"]
        self.__on_running = info_to_save["on_running"]
        self.__on_connect = info_to_save["on_connect"]
        self.device_type = info_to_save["device_type"]
        self.action.clear()
        self.__set_action_by_action_load()
        self.__topic_subscribe = info_to_save["topic_subscribe"]
        if self.__on_running:
            self.__on_running = False
            self.run(self.device_type, self.host, self.port)
            for topic in self.__topic_subscribe:
                self.subscribe(topic, self.qos)
                self.topic_in_use.add(topic)
        return 0

    def save_to_config(self, config_file_path = None):
        """
            此函数需要与提供的load_from_config一起使用 | NEED load_from_config Function
            config_file_path：的默认位置是同级目录下的config.json | configure_file_path: Default location is the config.json in the same directory
        """
        config_file_path = config_file_path if config_file_path else self.__config_file_path
        info_to_save = {}
        info_to_save["client_id"] = self.client_id
        info_to_save["action_load"] = self.action_load
        info_to_save["action_func_name"] = self.action_func_name
        info_to_save["host"] = self.host
        info_to_save["port"] = self.port
        info_to_save["keepalive"] = self.keepalive
        info_to_save["topic"] = copy.deepcopy(self.topic)
        info_to_save["topic"]["2device"] = list(info_to_save["topic"]["2device"])
        info_to_save["topic"]["2app_deivce"] = list(info_to_save["topic"]["2app_deivce"])
        info_to_save["device_pair_app2device"] = self.device_pair_app2device
        info_to_save["device_pair_device2app"] = self.device_pair_device2app
        info_to_save["use_quick_search"] = self.use_quick_search
        info_to_save["qos"] = self.qos
        info_to_save["on_running"] = self.__on_running
        info_to_save["on_connect"] = self.__on_connect
        info_to_save["device_type"] = self.device_type
        info_to_save["topic_subscribe"] = self.__topic_subscribe
        with open(config_file_path,'w') as f:
            f.write(json.dumps(info_to_save))
        

    def add2device_topic(self,topic):
        if topic and str(topic) not in self.topic_in_use:
            self.topic_in_use.add(topic)
            self.topic["2device"].add(topic)

    def add2app_device_topic(self,topic):
        if topic and str(topic) not in self.topic_in_use:
            self.topic_in_use.add(topic)
            self.topic["2app_deivce"].add(topic)

    def add_app_device_id_pair(self, appid, deviceid):
        if appid or deviceid:
            return -1
        # 如果这个id对在双方的键值表中都有，说明无需添加 | If ID is in the key-value tables between C/S, the id neeed not to add
        if appid in self.device_pair_app2device.keys() and \
            deviceid in self.device_pair_device2app.keys():
            return -1
        if appid in self.device_pair_app2device.keys():
            self.device_pair_app2device[appid].append(deviceid)
        else:
            self.device_pair_app2device[appid].append([deviceid])

        if deviceid in self.device_pair_device2app.keys():
            self.device_pair_device2app[deviceid].append(appid)
        else:
            self.device_pair_device2app[deviceid].append([appid])
        return 0



    def change_2server_topic(self,topic):
        if topic and str(topic) not in self.topic_in_use:
            self.topic_in_use.add(topic)
            self.topic_in_use.remove(self.topic["2server"])
            self.topic["2server"] = topic

    def send2server(self,msg):
        if self.__on_connect:
            self.publish(self.topic["2server"],str(msg))

    def __check_func_can_be_add(self,action):
        if not (action and callable(action)):
            return -1
        action_def_path = action.__code__.co_filename
        action_def_relpath = os.path.relpath(action_def_path)
        if action_def_relpath[:2] is "..":
            return -1
        if action.__code__.co_argcount > 2:
            return -1
        return 0

    
    
    def add_action(self,action,action_name=None):
        """
            一个接口的添加函数，其添加客户端执行的接口集合 | A Function used to add Interface which add a set of actions Server perform
            当客户端接收到消息时，会调用on_message回调，此回调请不要覆盖，其依据接收的消息调用 | Do NOT cover the on_message call according to received message 
                                                                                          when Sever receives message
            self.action中的函数 | Functions in self.action

            当满足msg.payload.split()[0]在self.action的keys中时，会调用此key对应的action函数 | When msg.payload.split()[0] is satisfied in the keys of self.action, 
                                                                                            the action function corresponding to this key will be called 

            action：添加的函数，目前没有专门设定函数的输入，请先默认不使用输入 | action: Added functions, default is no input ( NO specially setting function input currently )
            action_name：添加的键值，以此键值作为调用的依据，如果为None就使用函数本身的名字 | action_name: Added key-value, use key-value to call function, None means the name of function

            action要求： | Request of action
                1.目前参数的数量不要超过2个，对应的位置会传入对应参数 | The number of parameters is less or equal to 2, Pass in the corresponding parameters at the corresponding position
                2.返回值可以为空，但如果返回请使用str类型 | Function could reutrn to Null, if not, Please return to str type
                3.有返回值时，格式约定为\"topic 实际返回值\"，topic指定你发送的目标，实际返回值为你希望发送的信息 | If function returns str type, its Format is
                                                                                                             \"topic return value\", the real return value is
                                                                                                             the message you wanted to send

            action参数要求： | Request of parameters of action
                1.如果没有参数，就直接调用 | If function have NO parameter, please call directly
                2.如果只有一个参数，只传递msg，也就是MQTTmessage类 | If function have single parameter, Please pass the msg ( MQTTmessage Class )
                3.如果有两个参数，则第一个参数传递msg，第二个参数传递device_interface的实例 | If function have 2 parameter, The first passes msg, 
                                                                                         The second passes instance of device_interface

        """
        if self.__check_func_can_be_add(action) != 0:
            return -1
        action_func_name = action.__name__
        action_name = action_name if action_name else action_func_name
        action_def_path = action.__code__.co_filename
        self.action_load[action_func_name] = action_def_path
        self.action[action_name] = action
        self.action_func_name[action_func_name] = action_name
        return 0

    def add_action2(self, action):
        self.add_action(action)
        return action

    def set_default_action(self, action):
        if self.__check_func_can_be_add(action) != 0:
            return -1
        self.default_func = action
        self.default_func_path = action.__code__.co_filename



    def send_ret2topic(self,ret):
        """
            此函数负责处理返回值发送，ret格式参考addAction给出的格式

            ret:Action函数返回的值，负责给指定topic发送信息

            如果指定的topic不在使用列表当中，此函数不会发送任何消息，目前topic列表还没有自动更新
        """
        topic = ret.split()[0]
        if topic in self.topic_in_use:
            self.publish(topic,ret[len(topic):],qos=self.qos)

    def search_exct_api_by_str(self,msg):
        """
            根据订阅topic返回的信息执行函数，此函数不应该被直接调用 | Execution function according to the message ruturned from subscrible topic 
            msg：mqtt返回的信息，包括topic和payload | msg: The returned message from MQTT, include Topic and Payload

            self.quick_search_for_api：
                1.True时，对于没有加空格的调用命令，也可以实现调用 | True: Calling commands without spaces can also be called
                2.False时，必须严格的按照格式发送消息 | False: Messages must be sent in strict accordance with the format
                3.此变量推荐为False | Recommend to set the variable to False
                4.不要在添加Action后再修改此值，会出错 | Do NOT update the value after add actions, or it will be cause an error
                5.功能暂未实现，请不要调用 | The feature is not yet implemented, please NOT call it
        """
        payload = str(msg.payload,encoding="utf-8")
        if msg.topic in self.topic_in_use:
            ret = None
            func = None
            if self.use_quick_search:
                self.quick_search_for_api(msg)
            else:
                # 对函数进行搜索，如果没找到则使用默认的函数进行处理 | search functions, if functions are not found, we will use default function to handle
                if payload.split()[0] in self.action.keys():
                    func = self.action[payload.split()[0]]
                elif self.default_func:
                    func = self.default_func
                # 依据函数的参数数量进行调用 | According to the numbers of functions parameters to call
                func_argc = func.__code__.co_argcount
                print("calling func name:",func.__name__)
                # print("using func:"+func.__name__+"\r\narg count is "+str(func_argc))
                if func_argc == 0:
                    ret = func()
                elif func_argc == 1:
                    ret = func(msg)
                elif func_argc == 2:
                    ret = func(msg, self)
                else:
                    raise BaseException("can not support args count more than 2 for now")
            if ret:
                self.send_ret2topic(ret)


    def build_quick_search(self,action,action_name=None):
        """
            使用quick_search_for_api的必要函数，构建查找表 | the necessary function to use quick_search_for_api to construct Look-Up Table

            不应该被外部调用 | Shold NOT call externaly
        """
        pass
    
    def quick_search_for_api(self,msg):
        """
            利用查找表，提升查找速度，针对的是不严格的接口形式 | Use Look-Up Table to speed search velocity, which consider the unstrict Interface Form

            严格实现的接口至少和search_exct_api_by_str一样快 | Use strict Interface Implement can be as fast as search_exct_api_by_str at least
        """
        pass

    def on_connect(self, mqttc, obj, rc):
        """
            建立和broker连接后的回调 | establish the recall function after Broker connectived

            rc==0 时表示正确的连接，请不要修改此函数 NOTE! Please not modify the function! rc == 0 implies the connection is correct
        """
        if rc == 0:
            logging.info(self._rc_mean[rc])
        elif rc in [1,2,3,4,5]:
            logging.error(self._rc_mean[rc])
            raise BaseException(self._rc_mean[rc])
        else:
            logging.error("unKown rc value with rc="+ str(rc))
            raise BaseException("Unkown rc value")
        
 
    def on_publish(self, mqttc, obj, mid):
        """
            成功发布消息后的回调 | recall function after publish message successfully
        """
        logging.info("OnPublish, mid: "+str(mid))

    
    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        """
            成功订阅后的回调 | recall function after subscrible topic successfully
        """
        logging.info("Subscribed: "+str(mid)+" "+str(granted_qos))
    
    def on_log(self, mqttc, obj, level, string):
        logging.info("Log:"+string)
    
    def on_message(self, mqttc, obj, msg):
        """
            获得订阅消息推送的回调函数，会依据消息执行函数 | Callback Function to obtain the subscrible message which wolud perform according to the message

            msg:订阅的topic,以及订阅的消息payload | msg: the subscrible topic, payload: the subscrible message

            请不要修改此函数 | NOTE! Please NOT modify the function
        """
        curtime = datetime.datetime.now()
        strcurtime = curtime.strftime("%Y-%m-%d %H:%M:%S")
        print("**************on_message***************")
        logging.info(strcurtime + ": " + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        self.search_exct_api_by_str(msg)

    def run(self,device_type,host,port):
        """
            客户端运行，其会新建一个线程，不会造成阻塞的问题 | Run Server, which will rebulid thread ( NOT cause blocking problem )
            请运行期间调用一次，不要多次调用 | Please call once during running process ( NOT call it repeatedly )
            device_type：设备的类型+命名，暂未使用 | device_type: the type of device and name ( NOT Used Temporarily)
            host：连接的broker服务器 | host: the connective Broker Server
            port：连接的broker服务器的mqtt服务端口 | port: the MQTT server port of connective Broker Server
        
        """
        # 设置账号密码（如果需要的话）| Set the User Name and Password ( if you need )
        #self.client.username_pw_set(username, password=password)
        if not self.__on_running:
            self.host = host
            self.port = port
            self.device_type = device_type
            self.connect(host, port, self.keepalive)
            self.loop_start()
            self.__on_running = True
        else:
            logging.error("the mqtt client is on running")

    def add_subscribe(self, topic, qos = 0, options=None, properties=None):
        """
            为了保证订阅在保存后可以自动恢复，请使用此函数订阅 | To ensure the subscription could recover after saving, Please use the function to subscrible topic

            注意，options 以及 properties 暂不支持 | NOTE! Options and properties is not currently supported
        """
        if topic:
            self.__topic_subscribe.append(topic)
            self.topic_in_use.add(topic)
            self.subscribe(topic, qos, options, properties)




if __name__ == '__main__':
    logging.basicConfig(filename="./test.log",format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.INFO)
    # t = device_interface()
    t2 = device_interface("test2")
    host = "52.184.15.163"
    port = 1883
    # t.run("123",host,port)
    t2.run("234",host,port)
    # t.subscribe("test",2)
    
    # time.sleep(1)
    # t2.publish("test","print_msg3 123456",2)
    # for i in range(100):
    #     t2.publish("test","time_test "+str(time.perf_counter()),2)
    #     time.sleep(1)
    # time.sleep(1000)
