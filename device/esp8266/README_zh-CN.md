# 设备接入
本模块是基于ESP8266实现的一个设备接入功能的子模块，主要的逻辑是：

1. 自动发射AP热点
2. 支持其他设备接入热点，并监听`8989`端口
3. 当收到包含`magic_number`字段的request报文，其会判断字段是否正确，若正确进入第4步
4. 依据request报文给出的AP热点，连接此热点，并向服务器发送设备添加的消息
5. 根据服务器回传的消息，若成功添加则结束，否则回到第一步

# 子模块说明
本模块包含了两个子模块：
+ `socket_test`目录下，`esp8266.py`是运行驱动的核心程序，其完成了设备接入的全部逻辑
+ `umqtt.simple`目录下，是一个mqtt client的实现，模块需要使用`umqtt`目录下的`simple.py`，这个文件完成了mqtt客户端的部分功能

# 使用说明
需要提前准备好ESP8266模块，然后在其上刷好micropython模块，同时需要准备micropythond的终端，方便文件的上传与修改。

之后参考如下步骤：
1. 将`socket_test/esp8266.py`和`umqtt_simple/umqtt/simple.py`两个文件上传到ESP8266
2. 修改ESP8266的`boot.py`文件，
    
    写入
    ```
    from esp8266 import main
    main()
    ```

3. 断开ESP8266，重新上电

如上，就可以完成在ESP8266接电后，自动执行设备接入的逻辑。