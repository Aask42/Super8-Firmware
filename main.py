from machine import I2C, Pin
import time
import uasyncio as asyncio
import gc
from sao.super8_i2c import Super8I2C
import json
from boot import i2c0, i2c1
from sao.init import init_config

counter = 0
## do a quick spiral to test
if petal_bus:
    for j in range(1):  # Adjust the range for the number of cycles you want
        # Forward wave
        for shift in range(8):
            which_leds = (1 << (shift + 1)) - 1
            for i in range(1, 9):
                #print(which_leds)
                petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
                time.sleep_ms(30)
            time.sleep_ms(10)  # Pause at the end of each wave

        # Reverse wave
        for shift in range(7, -1, -1):
            which_leds = (1 << (shift + 1)) - 1
            for i in range(1, 9):
                #print(which_leds)
                petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
                time.sleep_ms(30)
            time.sleep_ms(10)  # Pause at the end of each reverse wave
            # Clear all LEDs at the end of the cycle
            for i in range(1, 9):
                petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([0]))

def sub_cb(topic, msg, MQTT_CLIENT_ID, petal_bus):
    msg_string = msg.decode("UTF-8")
    #print(f"Received message: {msg_string} on topic: {topic.decode()} ")
    main_topic = f'user/{MQTT_CLIENT_ID}'
    print(f'main_topic: {main_topic} vs {topic.decode()}')
    if topic.decode() == main_topic or topic.decode() == "badge_broadcast":
       
        print("do stuff")
        #petal_bus = None
        if petal_bus:
            for j in range(1):  # Adjust the range for the number of cycles you want
                # Forward wave
                for shift in range(8):
                    which_leds = (1 << (shift + 1)) - 1
                    for i in range(1, 9):
                        #print(which_leds)
                        petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
                        time.sleep_ms(10)
                    time.sleep_ms(1)  # Pause at the end of each wave

                # Reverse wave
                for shift in range(7, -1, -1):
                    which_leds = (1 << (shift + 1)) - 1
                    for i in range(1, 9):
                        #print(which_leds)
                        petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
                        time.sleep_ms(10)
                    time.sleep_ms(1)  # Pause at the end of each reverse wave
                for i in range(1, 9):
                    petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([0]))
        try:
            init_config = json.loads(msg_string)
            #print(f"Attempting to use the config object {msg_string}")
            a = Super8I2C(i2c_busses=[i2c0, i2c1], device_config=init_config)
            a = None
        except:
            print("Issues talking to the i2c device...")
        """
        if petal_bus:
            for j in range(1):  # Adjust the range for the number of cycles you want
                # Forward wave
                for shift in range(8):
                    which_leds = (1 << (shift + 1)) - 1
                    for i in range(1, 9):
                        #print(which_leds)
                        petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
                        time.sleep_ms(10)
                    time.sleep_ms(1)  # Pause at the end of each wave

                # Reverse wave
                for shift in range(7, -1, -1):
                    which_leds = (1 << (shift + 1)) - 1
                    for i in range(1, 9):
                        #print(which_leds)
                        petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
                        time.sleep_ms(10)
                    time.sleep_ms(1)  # Pause at the end of each reverse wave
                for i in range(1, 9):
                    petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([0]))
            """
    
async def main():
    from CONFIG.MQTT_CONFIG import MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, MQTT_SERVER
    from CONFIG.WIFI_CONFIG import WIFI_LIST
    
    from src.wifi_manager import WiFiConnection
    from src.mqtt_manager import MQTTManager
    gc.enable()
    # Known SAO HALs
    #from sao.super8_petal import Super8Petal

    #sao_super8_petal = Super8Petal([i2c0, i2c1], 0x00)
    #sao_super8_petal.illuminate_all_segments()
    Super8I2C(i2c_busses=[i2c0, i2c1], device_config=init_config)
    if "YOURWIFINETWORK" != WIFI_LIST[0][0]:
        wifi_manager = WiFiConnection()
        await wifi_manager.main()
        
        if MQTT_USERNAME != b"YOURUSERNAME":
            mqtt_manager = MQTTManager(MQTT_SERVER, MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD)
            await mqtt_manager.main(wifi_manager)  # Ensure the MQTT waits for WiFi connection
            mqtt_manager.set_callback(lambda topic, msg: sub_cb(topic, msg, MQTT_CLIENT_ID, petal_bus))

            await mqtt_manager.subscribe(f'user/{MQTT_CLIENT_ID}')
            await mqtt_manager.subscribe(f'badge_broadcast')

        else:
                print("Please configure your MQTT server to control over the internet")
    else:
        print("Please configure your WIFI to connect to the internet")
    while True:
        gc.collect()
        await asyncio.sleep_ms(100)

asyncio.run(main())


