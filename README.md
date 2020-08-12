# Smart_Lock

This is a Smart_Lock Project using Ultra96_V2 and PYNQ.

如果你想要中文文档，请点击这里[中文文档](README_zh-CN.md)

## Project Description

This project is a smart door lock system based on MQTT, Flutter, Dlib and Ultra 96 boards. The APP side has the functions of adding devices, remote control, and video streaming. The device side can recognize strangers and take pictures and send back and support multi-user operations. The server side is responsible for operations such as communication between devices.

> You can find the latest version in our [team repository](https://github.com/XilinxCannonFodderTeam/smart_lock)

## Quick Start

The setup of this project has not been tested, so the correct execution is not guaranteed. It is recommended to directly download the entire project and configure the app, device and server side by step.

Open your Ultra96 terminal, make sure it is connected to the Internet, and enter:

```bash
sudo pip3 install upgrade git+https://github.com/XilinxCannonFodderTeam/smart_lock.git
```

> Note: This project currently uses the dlib library. Because the dlib library is relatively large, the compilation time is longer.

## Future Plan

### New Features

1. Allow python functions to be uploaded and then automatically added to the callback support
2. Add device and app pair instead of adding manually
3. Support automatic restart, restart directly when an error occurs
4. Use thread pool to optimize the asynchronous call of callback

## Contact Us

If you have any questions or problems, please contact us.
Email Address: <664696421@qq.com>

## Project Structure

The project is divided into device side, APP side and server side

### device

The open source OpenCV, dlib, and ffmpeg libraries are mainly used.

It contains [face_server](#face_server), [RTMP](#rtmp), [esp8266](device/esp8266/README.md) module.

### APP

Mainly use Dart programming language and flutter framework.

> Note: Our APP is provided as a submodule in this repository, please use the relevant submodule command to download.

### server

Mainly use Python programming language, paho-mqtt and Flask framework.

You can find the documentation under the corresponding [directory](server/README.md)

## Module specification

### face_server

This module is mainly used for face recognition.

The face_api module is developed based on OpenCV and dlib.

> Before the project runs, you need to download a picture of the smart lock owner in the directory

First, the detect, encode_face function is introduced from this module to detect and encode faces, and then the matplotlib and time libraries are introduced to display the captured images in the Jupyter Notebook environment and measure the recognition time.

#### Load the owner's picture and encode

```python
encode_face('owner.jpg')
img_lists = []
```

Use encode_face to load the picture of the smart lock owner, and then create an empty list img_list to store the pictures taken by the camera.

#### Capture and recognize face images

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

In the Demo, set to intercept 4 portrait pictures, with an interval of 0.1 seconds between each interception, save the intercepted pictures into the img_list list through the list.append method, if the smart lock owner is recognized, output Find + loaded image face ID, otherwise output Find Stranger.

#### Display face image in notebook

```python
for i in img_lists:
    plt.figure()
    plt.imshow(i)
```

After recognition, use pyplot.figure and pyplot.imshow to display the captured face image.

### RTMP

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
