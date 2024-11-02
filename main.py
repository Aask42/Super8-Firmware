from machine import I2C, Pin
import time
import uasyncio as asyncio

counter = 0

## do a quick spiral to test

          
def sub_cb(topic, msg):
    msg_string = msg.decode("UTF-8")
    print(f"Received message: {msg} on topic: {topic.decode()} ")
    
    if topic == b'light_wheel':
        print("do light wheel stuff")
        if petal_bus:
            for j in range(8):
                which_leds = (1 << (j+1)) - 1 
                for i in range(1,9):
                    print(which_leds)
                    petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
                    time.sleep_ms(30)
                    petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))

async def main():
    from CONFIG.MQTT_CONFIG import MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, MQTT_SERVER
    from CONFIG.WIFI_CONFIG import WIFI_LIST
    
    from src.wifi_manager import WiFiConnection
    from src.mqtt_manager import MQTTManager
    
    if "YOURWIFINETWORK" != WIFI_LIST[0][0]:
        wifi_manager = WiFiConnection()
        await wifi_manager.main()
        
        if MQTT_USERNAME != b"YOURUSERNAME":
            mqtt_manager = MQTTManager(MQTT_SERVER, MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD)
            await mqtt_manager.main(wifi_manager)  # Ensure the MQTT waits for WiFi connection
            mqtt_manager.set_callback(lambda topic, msg: sub_cb(topic, msg))

            await mqtt_manager.subscribe(b'light_wheel')
        else:
            print("Please configure your MQTT server to control over the internet")
    else:
        print("Please configure your WIFI to connect to the internet")
    while True:
        await asyncio.sleep_ms(100)

asyncio.run(main())
    
'''
## display button status on RGB
if petal_bus:
    if not buttonA.value():
        petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
    else:
        petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))

    if not buttonB.value():
        petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
    else:
        petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))

    if not buttonC.value():
        petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x80]))
    else:
        petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x00]))

## see what's going on with the touch wheel
if touchwheel_bus:
    tw = touchwheel_read(touchwheel_bus)

## display touchwheel on petal
if petal_bus and touchwheel_bus:
    if tw > 0:
        tw = (128 - tw) % 256 
        petal = int(tw/32) + 1
    else: 
        petal = 999
    for i in range(1,9):
        if i == petal:
            petal_bus.writeto_mem(0, i, bytes([0x7F]))
        else:
            petal_bus.writeto_mem(0, i, bytes([0x00]))



time.sleep_ms(20)
bootLED.off()
'''







