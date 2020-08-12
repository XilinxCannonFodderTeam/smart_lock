# 智能锁

## 项目说明

本项目是基于MQTT，Flutter以及Dlib和Ultra 96板卡的智能门锁系统。APP端具有添加设备、远程控制以及视频串流的功能，设备端能够识别陌生人后拍照回传并且支持多用户操作，服务器端则负责设备间通信等操作。

> 你可以在我们的[团队仓库](https://github.com/XilinxCannonFodderTeam/smart_lock)中找到最新版本

## Quick Start

本项目的setup没有经过测试，所以不保证正确执行，建议直接git下整个项目后按步骤依次对app,device和server端进行配置。

打开你的Ultra96的终端，确保联网，输入：

```bash
sudo pip3 install upgrade git+https://github.com/XilinxCannonFodderTeam/smart_lock.git
```

> 注意：本项目目前使用dlib库，由于dlib库较为庞大，编译时间较长。

## 未来计划

### 考虑进一步添加的功能

1. 允许上传python函数，然后自动添加到回调的支持当中
2. 设备和app对的添加，而非手工加入
3. 支持自动重启，当出现错误推出时直接重启
4. 对回调的异步调用，使用线程池进行优化

## 联系我们

如果你有任何问题，请联系我们。邮件地址: <664696421@qq.com>

## 项目结构

项目分为设备端、APP端和服务器端

### 设备端

主要使用了开源的OpenCV、dlib、ffmpeg库。

它包含有[face_server](#face_server)、[RTMP](#rtmp)、[esp8266](device/esp8266/README_zh-CN.md)模块。

### APP端

主要使用Dart编程语言和flutter框架。

> 注意：我们的APP在本仓库中作为子模块提供，请使用相关的submodule命令下载。

### 服务器端

主要使用Python实现，基于paho-mqtt和Flask框架

你可以在相应[目录](server/README_zh-CN.md)下找到说明文档

## 模块说明

### face_server

这个模块主要用于人脸识别。

基于 OpenCV 和 dlib 开发了 face_api 模块。

>项目运行前需要在目录下载入一张智能锁主人的图片

首先从该模块中引入 detect, encode_face 函数用于检测人脸，编码人脸，再引入 matplotlib 与 time 库用于在 Jupyter Notebook 环境下显示拍摄的图像并测量识别时间。

#### 载入主人图片并编码

```python
encode_face('owner.jpg')
img_lists = []
```

使用 encode_face 载入智能锁主人的图片，再创建一个空列表 img_list 用于存储摄像头拍摄的图片。

#### 截取人脸图像并识别

```python
i = 0
while i < 4:
    time.sleep(0.1)
    img,face_id = detect(0)
    img_lists.append(img)
    i += 1
    if not face_id:
        print("Find Stranger!")
    else:
        print("Find ",face_id)
```

在 Demo 中，设定截取4张人像图片，每次截取之间间隔0.1秒，将截取的图片通过 list.append 方法存入 img_list 列表，若识别到智能锁主人，则输出 Find + 载入图像的 face ID，否则输出 Find Stranger。

#### 在笔记本显示人脸图像

```python
for i in img_lists:
    plt.figure()
    plt.imshow(i)
```

可在识别后，使用 pyplot.figure 和 pyplot.imshow 显示拍摄到的人脸图像。

### RTMP

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
