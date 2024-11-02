from machine import I2C

class Super8Petal:
    def __init__(self, i2c_busses, i2c_address):
        self.i2c_bus = None
        self.i2c_address = i2c_address

        self.configure(i2c_busses)

    def bootstrap(i2c_bus, i2c_address):
        i2c_bus.writeto_mem(i2c_address, 0x09, bytes([0x00]))  ## raw pixel mode (not 7-seg) 
        i2c_bus.writeto_mem(i2c_address, 0x0A, bytes([0x09]))  ## intensity (of 16) 
        i2c_bus.writeto_mem(i2c_address, 0x0B, bytes([0x07]))  ## enable all segments
        i2c_bus.writeto_mem(i2c_address, 0x0C, bytes([0x81]))  ## undo shutdown bits 
        i2c_bus.writeto_mem(i2c_address, 0x0D, bytes([0x00]))  ##  
        i2c_bus.writeto_mem(i2c_address, 0x0E, bytes([0x00]))  ## no crazy features (default?) 
        i2c_bus.writeto_mem(i2c_address, 0x0F, bytes([0x00]))  ## turn off display test mode 

    def configure(self, i2c_busses):
        for bus in i2c_busses:
            try:
                self.bootstrap(bus, self.i2c_address)
                self.i2c_bus = bus
                break
            except:
                pass
        if not self.i2c_bus:
            print(f"Warning: Petal not found.")
      
    def illuminate_all_segments(self):
        self.i2c_bus.writeto_mem(self.i2c_address, 0x0B, bytes([0x07]))
        