"""
Written by: Amelia Wietting
Date: 20240730
For: DEF CON 32
Description: WiFi Connection Library for DC32 Infinite Wifi Portal
"""

from CONFIG.WIFI_CONFIG import WIFI_LIST, MAX_WIFI_CONNECT_TIMEOUT
import network
import uasyncio
import gc

class WiFiConnection:
    def __init__(self):
        self.wifi_connected = False
        
        self.wlan = network.WLAN(network.STA_IF)
        if getattr(self.wlan, 'scan_non_blocking', None):
            print("Using the custom scanning method")
            self.custom_scan = True
        else:
            print("Not using the custom scanning method")
            self.custom_scan = False
        self.network_count = 1
        
    def start_wifi_card(self):
        self.wlan.active(True)
        print("WiFi card initialized")

    async def connect_to_wifi(self):
        self.wifi_connected = False
        connection_attempts = 0

        try:
            if self.custom_scan:
                self.wlan.scan_non_blocking(blocking=False)
                #await uasyncio.sleep_ms(10)
                while self.wlan.in_progress():
                    await uasyncio.sleep_ms(200)
                    continue
                nets = self.wlan.results()
            else:
                nets = self.wlan.scan()

            print(nets)
            self.network_count = len(nets)
            for net in nets:
                for network_config in WIFI_LIST:
                    ssid_to_find = network_config[0]
                    if ssid_to_find == net[0].decode('utf-8'):
                        print(f'Attempting to connect to SSID: {ssid_to_find}')
                        if len(network_config) == 1:
                            self.wlan.connect(ssid_to_find)
                        else:
                            self.wlan.connect(ssid_to_find, network_config[1])
                      
                        while not self.wlan.isconnected():
                            connection_attempts += 1
                            await uasyncio.sleep(1)
                            if connection_attempts > MAX_WIFI_CONNECT_TIMEOUT:
                                print("Exceeded MAX_WIFI_CONNECT_TIMEOUT!")
                                break
                        
                        if self.wlan.isconnected():
                            self.wifi_connected = True
                            print('WLAN connection succeeded!')
                            break
                if self.wifi_connected:
                    break
        except Exception as e:
            print(f"Setup failed: {e}")

    async def setup_wireless(self):
        self.start_wifi_card()
        await self.connect_to_wifi()
        if not self.wifi_connected:
            print('Failed to connect to WiFi')
        else:
            print('WiFi connected successfully')

    async def update_network_count(self):
        while True:
            nets = []
            if self.custom_scan:
                self.wlan.scan_non_blocking(blocking=False)
                #await uasyncio.sleep_ms(10)
                while self.wlan.in_progress():
                    await uasyncio.sleep_ms(200)
                    continue
                nets = self.wlan.results()
            else:
                nets = self.wlan.scan()
            self.network_count = len(nets)
            await uasyncio.sleep(10)
            
    async def check_connections(self):
        while True:
            if not self.wlan.isconnected():
                print('WiFi disconnected, attempting to reconnect...')
                self.wlan.active(False)  # Deactivate the WiFi interface
                await uasyncio.sleep(1)  # Wait a bit before reinitializing
                self.start_wifi_card()  # Reactivate the WiFi interface
                await uasyncio.sleep(1)  # Wait a bit before reinitializing

                await self.connect_to_wifi()  # Attempt to reconnect
                gc.collect()
            await uasyncio.sleep(10)

    async def main(self):
        
        await self.setup_wireless()
        uasyncio.create_task(self.check_connections())
       
