# crystal_ball
A fun electronics project to make a witch's staff!

# 3d-Model
This is what the initial sketch was, and the 3d-model:  
![sketch](./assets/20240822_225214.jpg)  
![3d-model](./assets/crystal_ball.png)

The dome was quite tricky to 3d print because it is so thin (0.4mm) to allow light through. I printed it at 0.05mm layer height, with extra perimeters if needed and extra perimeter on overhands enabled in prusa-slicer.

# hardware
I used parts that I had lying around, namely some Adafruit through-hole Neopixels and a Pi Pico W. It wasn't pretty but worked.  
![hardware](./assets/20240822_215310.jpg)  
![hardware2](./assets/20240822_215313.jpg)  

# code
I used Adafruit's circuit python and neopixel library. I made a webapp that can cycle through 2 modes of animations
, and brightness. Used this guide for webapp [here](https://learn.adafruit.com/pico-w-http-server-with-circuitpython/create-your-settings-toml-file). Relies on adafruit_httpserver and neopixel.mpy. 