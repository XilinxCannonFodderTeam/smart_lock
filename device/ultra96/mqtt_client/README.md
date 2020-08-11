# Device end module
The module on the device side contains four parts, as follows:
1. `mqtt_client.py`, used to package the basic operation of mqtt, which is consistent with the server side
2. `face_api.py`, used for interface packaging related to face detection
3. `led.py`, a function wrapper used to turn on and off led
4. `device.py`, the running py program on the device side

# Run
To run the module, just switch to `./device/mqtt_client/`, and then run:
```
sudo python3 device.py
```