# code

The code uses circuit python. For hardware we use an ESP32 V2 Feather from Adafruit.

Installing circuit python is a bit of a pain, but [this](https://learn.adafruit.com/circuitpython-with-esp32-quick-start/installing-circuitpython) guide helps. I used [esptool](https://docs.espressif.com/projects/esptool/en/latest/esp32/index.html#quick-start) to flash circuit python, installed [thonny](https://thonny.org/) and pointed it to my circuit python port as the interpreter. Used thonny to copy the the adafruit libraries for `neopixel` and `adafruit_httpserver`. From there I used thonny to edit the`settings.toml to include wlan details (example below). Then I used thonny to copy my code across.

```
(virtual_env) D:\ziegl\git\crystal_ball>esptool.py --port COM15 erase_flash
esptool.py v4.7.0
Serial port COM15
Connecting.......
Detecting chip type... Unsupported detection protocol, switching and trying again...
Connecting....
Detecting chip type... ESP32
Chip is ESP32-PICO-V3-02 (revision v3.0)
Features: WiFi, BT, Dual Core, 240MHz, Embedded Flash, Embedded PSRAM, VRef calibration in efuse, Coding Scheme None
Crystal is 40MHz
MAC: e8:9f:6d:30:66:6c
Uploading stub...
Running stub...
Stub running...
Erasing flash (this may take a while)...
Chip erase completed successfully in 20.7s
Hard resetting via RTS pin...
```

```
(virtual_env) D:\ziegl\git\crystal_ball>esptool.py --port COM15 write_flash -z 0x0 D:\ziegl\Downloads\adafruit-circuitpython-adafruit_feather_esp32_v2-en_US-9.1.3.bin
esptool.py v4.7.0
Serial port COM15
Connecting....
Detecting chip type... Unsupported detection protocol, switching and trying again...
Connecting....
Detecting chip type... ESP32
Chip is ESP32-PICO-V3-02 (revision v3.0)
Features: WiFi, BT, Dual Core, 240MHz, Embedded Flash, Embedded PSRAM, VRef calibration in efuse, Coding Scheme None
Crystal is 40MHz
MAC: e8:9f:6d:30:66:6c
Uploading stub...
Running stub...
Stub running...
Configuring flash size...
Flash will be erased from 0x00000000 to 0x001b4fff...
Compressed 1789264 bytes to 1174886...
Wrote 1789264 bytes (1174886 compressed) at 0x00000000 in 103.3 seconds (effective 138.6 kbit/s)...
Hash of data verified.

Leaving...
Hard resetting via RTS pin...
```

Example settings.toml
```
SSID_NAME="crystal_ball"
WLAN_PASS="change_me"
```