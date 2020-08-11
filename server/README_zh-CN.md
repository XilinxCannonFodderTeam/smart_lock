# 服务器实例
本模块是基于Flask和mqtt协议实现的支持app与设备接入和管理的服务器端模块。模块的功能包含有：
1. 支持设备的添加
2. 支持远程的发送开关锁（开关灯）的命令
3. 实现了服务器端状态的保存与恢复
4. 实现了远程动态添加代码

其中3和4没有启用，仅实现了功能。

# 模块的结构
本模块包含`mqtt_client.py`和`server2.py`两个部分，前者基于mqtt进行了一些扩展，方便后续的开发，后者是一个简单的服务器端实例。

## mqtt_client
包含一个基于`paho.mqttm.client.Client`实现的`device_interface`类，主要的功能如下。
### 动作的添加
动作本质是python当中的函数，当有订阅的消息收到时，模块会将消息的payload的第一个单词作为key去查找动作表，如果找到一个对应的函数，那么就尝试调用此函数，函数的要求是接收的参数不超过2个，同时规定第一个参数为`paho.mqtt`中的msg消息，第二个参数为类本身，而返回值则约定如果没有返回值，则什么也不执行，否则，将返回值转换为`string`类型，然后依据第一个单词作为topic发送消息。

其中添加动作的函数如下：
```python
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
    if self.__check_func_can_be_add(action) != 0:
        return -1
    action_func_name = action.__name__
    action_name = action_name if action_name else action_func_name
    action_def_path = action.__code__.co_filename
    self.action_load[action_func_name] = action_def_path
    self.action[action_name] = action
    self.action_func_name[action_func_name] = action_name
    return 0

```
`__check_func_can_be_add`的作用是检测传入的参数是否是callable的，以及避免接口滥用，所以检测传入的对象所属的文件是否是当前项目的下。

`add_action`则是添加动作的接口函数，`action`必须是
### 状态的恢复与保存
由于是一个简单的项目，所以状态恢复与保存都是存储在json文件当中，没有将设备的topic存入数据库，相应的代码如下。

其中状态的恢复代码如下：
```python
def load_from_config(self, config_file_path = None):
    """
        此函数需要与提供的save_to_config一起使用
        config_file_path：的默认位置是同级目录下的config.json
        return：返回0表示成功的从配置文件导入,否则为失败
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
```
状态的保存如下：
```python
def save_to_config(self, config_file_path = None):
    """
        此函数需要与提供的load_from_config一起使用
        config_file_path：的默认位置是同级目录下的config.json
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
```

### 远程添加代码与动态导入


### 单例模式的支持

## server2
