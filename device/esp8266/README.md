# Device access
This module is a sub-module of device access function based on ESP8266. 

如果你想要中文文档，请点击这里[中文文档](README_zh-CN.md)

The main logic is:

1. Automatically launch AP hotspots
2. Support other devices to access the hotspot and monitor port `8989`
3. When it receives a request message containing the `magic_number` field, it will judge whether the field is correct, and if it is correct, go to step 4.
4. According to the AP hotspot given by the request message, connect to this hotspot and send the device added message to the server
5. According to the message returned by the server, it will end if it is successfully added, otherwise it will return to the first step

# Submodule description
This module contains two sub-modules:
+ In the `socket_test` directory, `esp8266.py` is the core program for running the driver, which completes all the logic of device access
+ The `umqtt.simple` directory is an implementation of mqtt client. The module needs to use `simple.py` in the `umqtt` directory. This file completes part of the functions of the mqtt client

# Instructions for use
You need to prepare the ESP8266 module in advance, and then flash the micropython module on it. At the same time, you need to prepare a micropythond terminal to facilitate file upload and modification.

Then refer to the following steps:
1. Upload the two files `socket_test/esp8266.py` and `umqtt_simple/umqtt/simple.py` to ESP8266
2. Modify the `boot.py` file of ESP8266,
    
    Write
    ```
    from esp8266 import main
    main()
    ```

3. Disconnect ESP8266 and power on again

As above, after ESP8266 is powered on, the logic of device connection can be automatically executed.

