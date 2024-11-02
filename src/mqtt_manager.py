from umqtt.simple import MQTTClient
import uasyncio as asyncio
from CONFIG.MQTT_CONFIG import MQTT_USERNAME, MQTT_PASSWORD, MQTT_CLIENT_ID, MQTT_SERVER

class MQTTManager:
    def __init__(self, server, client_id, username=None, password=None):
        self.server = server
        self.client_id = client_id
        self.username = username
        self.password = password
        self.client = MQTTClient(
            client_id=self.client_id,
            server=self.server,
            user=self.username,
            password=self.password
        )
        self.mqtt_connected = False
        self.subscriptions = []  # List to keep track of subscriptions

    def set_callback(self, callback):
        self.client.set_callback(callback)

    async def connect(self):
        try:
            print("Attempting to connect to the mqtt broker")
            self.client.connect()
            self.mqtt_connected = True
            print(f'Connected to {self.server} MQTT broker')
            # Resubscribe to all topics
            for topic in self.subscriptions:
                await self.subscribe(topic)
        except Exception as e:
            print(f'Error connecting to {self.server} MQTT broker: {e}')
            self.mqtt_connected = False
    
    async def subscribe(self, topic):
        if topic not in self.subscriptions:
            self.subscriptions.append(topic)
        if self.mqtt_connected:
            try:
                self.client.subscribe(topic)
                print(f'Subscribed to {topic} topic')
            except Exception as e:
                print(f'Error subscribing to {topic} topic: {e}')

    async def publish(self, topic, message):
        if self.mqtt_connected:
            try:
                self.client.publish(topic, message)
                print(f'Published message to {topic} topic: {message}') 
            except Exception as e:
                print(f'Error publishing to {topic} topic: {e}')

    async def check_messages(self):
        while True:
            if self.mqtt_connected:
                try:
                    self.client.check_msg()
                except Exception as e:
                    print(f'Error checking messages: {e}')
                    self.mqtt_connected = False
            await asyncio.sleep(0.5)

    async def reconnect_if_disconnected(self, wifi_connection):
        while True:
            if wifi_connection.wifi_connected and not self.mqtt_connected:
                print("WiFi reconnected, attempting to reconnect to MQTT broker")
                await self.connect()
            await asyncio.sleep(1)

    async def main(self, wifi_connection):
        # Ensure WiFi is connected before attempting MQTT connection
        while not wifi_connection.wifi_connected:
            print("Waiting for WiFi connection...")
            await asyncio.sleep(1)
        await self.connect()
        asyncio.create_task(self.check_messages())
        asyncio.create_task(self.reconnect_if_disconnected(wifi_connection))
