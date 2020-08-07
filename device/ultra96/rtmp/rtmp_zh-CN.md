# RTMP中文文档

If you want to read the English document, please check our [README](../../../README.md) on the homepage.

> 该项目运行前需要配置好Nginx服务器

## 如果已经配置好服务器

### 修改rtmp.py文件

将```localhost```改为你的服务器地址，然后将```port```改为你配置的端口

```python
rtmpUrl = "rtmp://localhost:port/videotest/test"
```

### 修改摄像头参数

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

### 运行

```bash
python rtmp.py
```

然后摄像头的图像便被串流到了服务器上

## 配置服务器

请参见Nginx相关文档

> 端口配置文件为```nginx.conf```, 已经增加了rtmp功能，请酌情修改

## 测试

```bash
sudo ffmpeg -re -i test.mp4 -vcodec copy -acodec copy -b:v 800k -b:a 32k -f flv rtmp://localhost:port/videotest/test
```
