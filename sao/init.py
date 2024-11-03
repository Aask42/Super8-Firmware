init_config = {
  "id": "00000000-0000-0000-0000-000000000000",
  "timestamp": "2024-11-03T00:00:00.000000000Z",
  "generator": "super8-web:0.1.0",
  "handle": "super8-petal",
  "type": "i2c",
  "i2c_address": 0,
  "init": [
    {
      "action": "i2c-write-mem",
      "i2c-mem-addr": 9,
      "payload": [0]
    },
    {
      "action": "i2c-write-mem",
      "i2c-mem-addr": 10,
      "payload": [9]
    },
    {
      "action": "i2c-write-mem",
      "i2c-mem-addr": 11,
      "payload": [7]
    },
    {
      "action": "i2c-write-mem",
      "i2c-mem-addr": 12,
      "payload": [129]
    },
    {
      "action": "i2c-write-mem",
      "i2c-mem-addr": 13,
      "payload": [0]
    },
    {
      "action": "i2c-write-mem",
      "i2c-mem-addr": 14,
      "payload": [0]
    },
    {
      "action": "i2c-write-mem",
      "i2c-mem-addr": 15,
      "payload": [0]
    },
    {
        # Write Red
      "action": "i2c-write-mem",
      "i2c-mem-addr": 2,
      "payload": [0]
    }
  ]
}