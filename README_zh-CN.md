# 智能锁

## 项目说明

本项目是基于MQTT，Flutter以及Dlib和Ultra 96板卡的智能门锁系统。APP端具有添加设备、远程控制以及视频串流的功能，设备端能够识别陌生人后拍照回传并且支持多用户操作，服务器端则负责设备间通信等操作。

## 未来计划

### 考虑进一步添加的功能

1. 允许上传python函数，然后自动添加到回调的支持当中
2. 设备和app对的添加，而非手工加入
3. 支持自动重启，当出现错误推出时直接重启
4. 对回调的异步调用，使用线程池进行优化

## 项目结构

项目分为设备端、APP端和服务器端

### 设备端

它包含有[RTMP](#rtmp)模块。

### APP端

### 服务器端

## 模块说明

### <a id="rtmp">RTMP</a>

这是视频串流模块

> 该项目运行前需要配置好Nginx服务器

#### 如果已经配置好服务器

##### 修改rtmp.py文件

将```localhost```改为你的服务器地址，然后将```port```改为你配置的端口

```python
rtmpUrl = "rtmp://localhost:port/videotest/test"
```

##### 修改摄像头参数

> 注意：受限于openCV自身，部分摄像头可能无法在Linux上成功被调用

如果你想要调用自带摄像头，则不用更改。

如果你想要调用其他摄像头，请把

```python
cap = cv.VideoCapture(0)
```

中的```0```改为```1```或```2```

```python
cap = cv.VideoCapture(1)
# or
cap = cv.VideoCapture(2)
```

如果你不能确定自己的摄像头参数，可以输入

```bash
ls /dev/vi*
```

这时你会得到相关摄像头信息，通过这个可以判断你的摄像头索引

##### 运行

```bash
python rtmp.py
```

然后摄像头的图像便被串流到了服务器上

#### 配置服务器

请参见Nginx相关文档

> 端口配置文件为```nginx.conf```, 请酌情修改

#### 测试

```bash
sudo ffmpeg -re -i test.mp4 -vcodec copy -acodec copy -b:v 800k -b:a 32k -f flv rtmp://localhost:port/videotest/test
```
