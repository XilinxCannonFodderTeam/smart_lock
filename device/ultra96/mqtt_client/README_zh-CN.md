# 设备端模块
设备端的模块包含了四个部分，如下：
1. `mqtt_client.py`，用于包装mqtt的基本操作，其和server端的一致
2. `face_api.py`，用于人脸检测相关的接口包装
3. `led.py`，用于点亮和熄灭led的函数包装
4. `device.py`，设备端的运行的py程序

# 运行
运行模块只需要切换到`./device/mqtt_client/`下，然后运行：
```
sudo python3 device.py
```

