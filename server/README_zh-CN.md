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

由于是一个简单的项目，所以状态恢复与保存都是存储在json文件当中，没有将设备的topic存入数据库，对应的状态保存的接口为`save_to_config`，而状态恢复的接口为`load_from_config`，默认从`./congif.json`中保存与读取。

### 远程添加代码与动态导入

这里的代码远程的写入是利用mqtt传输py文件实现的，只需要将`mqtt_client.py`中的`_save_input_py_file`添加到action列表就可以完成。

而动态导入则是将`mqtt_client.py`中的`_load_python_file`添加到action列表，然后就可以有此功能。

### 单例模式的支持

单例模式打开需要将`mqtt_client.py`中的`ON_SINGLE_PATTERN`置为True，然后就会在所有的线程中创建的`device_interface`都是同一个。

## server2

`server2.py`中的实现基于`mqtt_client`中的`device_interface`以及flask。

服务器的mqtt接口有：

1. lock：上锁的接口，此处实现是向所有设备发送上锁命令
2. unlock：开锁的接口，此处实现是向所有设备发送关锁命令
3. find_stranger：发现陌生人的接口，此接口执行向对应的topic发送陌生人发现的指令，并给出陌生人图片的链接
4. hand_shake：握手的接口，用于设备接入

flask实现啊的接口有：

1. `/hello`：用于测试服务器是否正确开启
2. `/lock`：和mqtt的`lock`一致
3. `/unlock`：和mqtt的`unlock`一致
4. `/test`：开锁和关锁的接口，依据upload的报文进行开锁或关锁
5. `/get_pic`：用于下载陌生人的图像