# Server instance
This module is a server-side module based on Flask and mqtt protocols that supports app and device access and management. 

如果你想要中文文档，请点击这里[中文文档](README_zh-CN.md)

The functions of the module include:
1. Support the addition of equipment
2. Support remote sending of switch lock (light switch) commands
3. Save and restore server-side state
4. Realize remote dynamic add code

Among them, 3 and 4 are not enabled, only the function is realized.

# Module structure
This module contains two parts: `mqtt_client.py` and `server2.py`. The former is based on mqtt with some extensions to facilitate subsequent development, and the latter is a simple server-side example.

## mqtt_client
Contains a `device_interface` class based on `paho.mqttm.client.Client` implementation. The main functions are as follows.
### Add action
The action is essentially a function in python. When a subscribed message is received, the module will use the first word of the payload of the message as the key to look up the action table. If a corresponding function is found, then it will try to call this function. The requirement is to receive no more than 2 parameters, while specifying that the first parameter is the msg message in `paho.mqtt`, the second parameter is the class itself, and the return value is agreed if there is no return value, then nothing Execute, otherwise, convert the return value to `string` type, and then send the message based on the first word as the topic.

The function for adding actions is as follows:
```python
def __check_func_can_be_add(self,action):
    if not (action and callable(action)):
        return -1
    action_def_path = action.__code__.co_filename
    action_def_relpath = os.path.relpath(action_def_path)
    if action_def_relpath[:2] is "..":
        return -1
    if action.__code__.co_argcount> 2:
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
The function of `__check_func_can_be_add` is to detect whether the passed-in parameter is callable, and to avoid interface abuse, so detect whether the file to which the passed-in object belongs is under the current project.

`add_action` is the interface function for adding actions, `action` must be
### State recovery and preservation
Since it is a simple project, the state restoration and saving are stored in json files, and the topic of the device is not stored in the database. The corresponding state saving interface is `save_to_config`, and the state restoration interface is `load_from_config`, Save and read from `./congif.json` by default.


### Remote add code and dynamic import
The remote writing of the code here is realized by using mqtt to transfer py files, and it can be completed by adding `_save_input_py_file` in `mqtt_client.py` to the action list.

The dynamic import is to add the `_load_python_file` in `mqtt_client.py` to the action list, and then you can have this function.

### Singleton mode support
To open singleton mode, you need to set the `ON_SINGLE_PATTERN` in `mqtt_client.py` to True, and then the `device_interface` created in all threads will be the same.


## server2
The implementation in `server2.py` is based on `device_interface` and flask in `mqtt_client`.

The mqtt interface of the server is:
1. lock: The interface for locking, the implementation here is to send a lock command to all devices
2. unlock: The interface for unlocking the lock, the implementation here is to send a lock command to all devices
3. find_stranger: An interface for finding strangers. This interface executes instructions to send strangers discovered to the corresponding topic, and gives links to pictures of strangers
4. hand_shake: Handshake interface, used for device access

Flask implements the following interfaces:
1. `/hello`: Used to test whether the server is started correctly
2. `/lock`: Same as mqtt's `lock`
3. `/unlock`: Same as mqtt's `unlock`
4. `/test`: The interface for unlocking and closing the lock, unlocking or closing the lock according to the upload message
5. `/get_pic`: Used to download images of strangers