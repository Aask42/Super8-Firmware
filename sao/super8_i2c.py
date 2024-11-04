# super8_i2c.py
from machine import I2C
from sao.init import init_config
import boot  # Import boot.py to access i2c0 and i2c1
import time
class Super8I2C:
    def __init__(self, i2c_busses, device_config=None):
        self.i2c_bus = None
        self.i2c_busses = i2c_busses
        self.device_config = device_config
        self.i2c_address = self.device_config.get('i2c_address', None)
        self.device_name = self.device_config.get('handle', 'unknown device')
        
        if self.i2c_address is not None:
            self.configure()
        else:
            print("No I2C address provided for device configuration.")

    def bootstrap(self, i2c_bus):
        # Attempt each init command in the configuration
        for item in self.device_config.get('commands', []):
            try:
                action = item.get("action")
                print(f'expected action: {action}')
                if action == "i2c-write-mem":
                    payload = bytes(item.get("payload", []))

                    i2c_mem_addr = item.get("i2c-mem-addr")
                    print(f"writing address {self.i2c_address} on address: {i2c_mem_addr} with this payload {payload}")

                    i2c_bus.writeto_mem(self.i2c_address, i2c_mem_addr, payload)
                elif action == "i2c-write":
                    payload = bytes(item.get("payload", []))
                    i2c_bus.writeto(self.i2c_address, payload)
                elif action == "delay":
                    delay_ms = int(item.get("duration_ms", []))
                    print(f"Delaying: {delay_ms}")
                    time.sleep_ms(delay_ms)
            except Exception as e:
                print(f"Error during bootstrap for {self.device_name} on I2C bus: {e}")
                raise  # Re-raise to stop if there's an issue with this bus

    def configure(self):
        # Try each bus until one succeeds or all fail
        for bus in self.i2c_busses:
            try:
                self.bootstrap(bus)
                self.i2c_bus = bus  # Set the working bus
                print(f"{self.device_name} successfully configured on I2C bus.")
                break  # Exit loop once configuration succeeds
            except Exception:
                continue  # Ignore errors and try the next bus
        
        if not self.i2c_bus:
            print(f"Warning: {self.device_name} not found on any I2C buses.")

# Instantiate Super8I2C with device configuration
#a = Super8I2C(i2c_busses=[boot.i2c0, boot.i2c1], device_config=init_config)

