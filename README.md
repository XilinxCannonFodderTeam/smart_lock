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

It contains [RTMP](#rtmp) module.

### APP

### server

## Module specification

### <a id="rtmp">RTMP</a>

This is the video streaming module

> The Nginx server needs to be configured before the project runs
