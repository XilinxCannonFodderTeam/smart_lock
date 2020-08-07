# Smart_Lock

This is a Smart_Lock Project using Ultra96_V2 and PYNQ.

如果你想要中文文档，请点击这里[中文文档](README_zh-CN.md)

## Project Description

This project is a smart door lock system based on MQTT, Flutter, Dlib and Ultra 96 boards. The APP side has the functions of adding devices, remote control, and video streaming. The device side can recognize strangers and take pictures and send back and support multi-user operations. The server side is responsible for operations such as communication between devices.

## Future Plan

### New Features

1. Allow python functions to be uploaded and then automatically added to the callback support
2. Add device and app pair instead of adding manually
3. Support automatic restart, restart directly when an error occurs
4. Use thread pool to optimize the asynchronous call of callback

## Project Structure

The project is divided into device side, APP side and server side

### device

The open source OpenCV, dlib, and ffmpeg libraries are mainly used.

It contains [face_server](#face_server), [RTMP](#rtmp) module.

### APP

Mainly use Dart programming language and flutter framework.

### server
Mainly use Python programming language, paho-mqtt and Flask framework

## Module specification

### <a id="face_server">face_server</a>

This module is mainly used for face recognition.

### <a id="rtmp">RTMP</a>

This is the video streaming module

> The Nginx server needs to be configured before the project runs

#### If the server has been configured

##### Modify the rtmp.py file

Change ```localhost``` to your server address, and then change ```port``` to the port you configured

```python
rtmpUrl = "rtmp://localhost:port/videotest/test"
```

##### Modify camera parameters

> Note: Due to openCV itself, some cameras may not be successfully called on Linux

If you want to call the built-in camera, there is no need to change it.

If you want to call USB-Camera or other cameras, please put ```0``` in

```python
cap = cv.VideoCapture(0)
```

to ```1``` or ```2```

```python
cap = cv.VideoCapture(1)
# or
cap = cv.VideoCapture(2)
```

If you are not sure of your camera parameters, you can enter

```bash
ls /dev/vi*
```

##### Run

```bash
python rtmp.py
```

Then the camera image is streamed to the server

#### Configure the server

Please refer to Nginx related documents

> The port configuration file is ```nginx.conf```, please modify as appropriate

#### Test

```bash
sudo ffmpeg -re -i test.mp4 -vcodec copy -acodec copy -b:v 800k -b:a 32k -f flv rtmp://localhost:port/videotest/test
```
