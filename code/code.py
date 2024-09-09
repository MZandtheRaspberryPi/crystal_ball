"""
Code to serve up a webserver that controls LEDs and toggles modes. Relies on some environment variables set in the settings.toml.
"""
import os
import time
import board
import microcontroller
from rainbowio import colorwheel
import neopixel

from adafruit_httpserver import Server, Request, Response, POST
import ipaddress
import wifi
import socketpool

SSID_NAME = os.getenv("SSID_NAME")
SSID_PASS = os.getenv("WLAN_PASS")
NUM_PIXELS = 10
LED_MODE = "rainbow"
BRIGHTNESS = 0.5
BRIGHTNESS_LOWER_BOUND = 0.2
BRIGHTNESS_UPPER_BOUND = 1.0
BRIGHTNESS_INCREMENT = 0.1
RAINBOW_SPEED = 0
RAINBOW_MIN_SPEED = 0
RAINBOW_MAX_SPEED = 0.1
RAINBOW_SPEED_INCREMENT = 0.002
COLOR_R = 255
COLOR_G = 0
COLOR_B = 255
COLOR_UPPER_BOUND = 255
COLOR_LOWER_BOUND = 0
COLOR_INCREMENT = 10
#  font for HTML
FONT_FAMILY = "monospace"

#  set static IP address
ipv4 =  ipaddress.IPv4Address("192.168.1.42")
netmask =  ipaddress.IPv4Address("255.255.255.0")
gateway =  ipaddress.IPv4Address("192.168.1.1")
wifi.radio.set_ipv4_address(ipv4=ipv4,netmask=netmask,gateway=gateway)
wifi.radio.start_ap(ssid=SSID_NAME, password=SSID_PASS)
print("started network")
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)

# Update this to match the number of NeoPixel LEDs connected to your board.
ORDER = neopixel.RGB
PIXEL_PIN = board.D5

pixels = neopixel.NeoPixel(
PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False, pixel_order=ORDER)

def web_page():
  html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-type" content="text/html;charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
html{{font-family: {FONT_FAMILY}; background-color: lightgrey;
display:block; margin: 0px auto; text-align: center;}}
	h1{{color: deeppink; padding: 2vh; font-size: 35px;}}
	p{{font-size: 1.5rem; display: block;}}
	.button{{font-family: {FONT_FAMILY};display: inline-block;
	background-color: black; border: none;
	border-radius: 4px; color: white; padding: 16px 40px;
	text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}}
	p.dotted {{margin: auto; display: block;
	width: 75%; font-size: 25px; text-align: center;}}
</style>
</head>
<body>
<title>Crystal Ball Web Server</title>
<h1>Crystal Ball Web Server</h1>
<div class="paragraph">
 <p class="dotted">This is a webserver to control the lights in the crystal ball.</p>
</div> 
<div class="paragraph">
 <p class="dotted">The current mode is <span style="color: deeppink;">{LED_MODE}</span></p>
</div>
<h1>Lights Control</h1>
<form accept-charset="utf-8" method="POST">
<button class="button" name="Set Rainbow Mode" value="rainbow_mode" type="submit">Set Rainbow</button></a></p></form>
<p><form accept-charset="utf-8" method="POST">
<button class="button" name="Set Color Pulse Mode" value="color_pulse_mode" type="submit">Set Color Pulse</button></a></p></form>
<p><form accept-charset="utf-8" method="POST">
<button class="button" name="Increment Brightness" value="increment_brightness" type="submit">Increment Brightness ({BRIGHTNESS_LOWER_BOUND} to {BRIGHTNESS_UPPER_BOUND}, increment: {BRIGHTNESS_INCREMENT}, currently: {BRIGHTNESS})</button></a></p></form>
<p><form accept-charset="utf-8" method="POST">
<button class="button" name="Increment Rainbow Speed" value="increment_rainbow_speed" type="submit">Increment Rainbow Speed ({RAINBOW_MIN_SPEED} to {RAINBOW_MAX_SPEED}, increment: {RAINBOW_SPEED_INCREMENT}, currently: {RAINBOW_SPEED})</button></a></p></form>
<p><form accept-charset="utf-8" method="POST">
<button class="button" name="Color Pulse: Red" value="red" type="submit">Increment Color Pulse Red ({COLOR_LOWER_BOUND} to {COLOR_UPPER_BOUND}, increment: {COLOR_INCREMENT}, currently: {COLOR_R})</button></a></p></form>
<p><form accept-charset="utf-8" method="POST">
<button class="button" name="Color Pulse: Green" value="green" type="submit">Increment Color Pulse Green ({COLOR_LOWER_BOUND} to {COLOR_UPPER_BOUND}, increment: {COLOR_INCREMENT}, currently: {COLOR_G})</button></a></p></form>
<p><form accept-charset="utf-8" method="POST">
<button class="button" name="Color Pulse: Blue" value="blue" type="submit">Increment Color Pulse Blue ({COLOR_LOWER_BOUND} to {COLOR_UPPER_BOUND}, increment: {COLOR_INCREMENT}, currently: {COLOR_B})</button></a></p></form>
<p><form accept-charset="utf-8" method="POST">
<button class="button" name="Reset Variables" value="reset_variables" type="submit">Reset All Variables to Defaults</button></a></p></form>
</body></html>
"""
  return html


#  route default static IP
@server.route("/")
def base(request: Request):  # pylint: disable=unused-argument
    #  serve the HTML f string
    #  with content type text/html
    return Response(request, f"{web_page()}", content_type='text/html')

def bound_number(cur, min_bound, max_bound, increment):
    new_val = cur + increment
    if new_val >= max_bound:
        new_val = min_bound
    return new_val

#  if a button is pressed on the site
@server.route("/", POST)
def buttonpress(request: Request):
    global LED_MODE, BRIGHTNESS, RAINBOW_SPEED, COLOR_R, COLOR_G, COLOR_B
    #  get the raw text
    raw_text = request.raw_request.decode("utf8")
    print(raw_text)
    if "rainbow_mode" in raw_text:
        LED_MODE = "rainbow"
    elif "color_pulse_mode" in raw_text:
        LED_MODE = "color_pulse"
    elif "increment_brightness" in raw_text:
        BRIGHTNESS = bound_number(BRIGHTNESS, BRIGHTNESS_LOWER_BOUND, BRIGHTNESS_UPPER_BOUND, BRIGHTNESS_INCREMENT)
        pixels.brightness = BRIGHTNESS
    elif "increment_rainbow_speed" in raw_text:
        RAINBOW_SPEED = bound_number(RAINBOW_SPEED, RAINBOW_MIN_SPEED, RAINBOW_MAX_SPEED, RAINBOW_SPEED_INCREMENT)
    elif "red" in raw_text:
        COLOR_R = bound_number(COLOR_R, COLOR_LOWER_BOUND, COLOR_UPPER_BOUND, COLOR_INCREMENT)
    elif "green" in raw_text:
        COLOR_G = bound_number(COLOR_G, COLOR_LOWER_BOUND, COLOR_UPPER_BOUND, COLOR_INCREMENT)
    elif "blue" in raw_text:
        COLOR_B = bound_number(COLOR_B, COLOR_LOWER_BOUND, COLOR_UPPER_BOUND, COLOR_INCREMENT)
    elif "reset_variables" in raw_text:
        LED_MODE = "rainbow"
        BRIGHTNESS = 0.5
        RAINBOW_SPEED = 0
        COLOR_R = 255
        COLOR_G = 0
        COLOR_B = 255
    else:
        pass
    return Response(request, f"{web_page()}", content_type='text/html')

def rainbow(speed):
    for j in range(255):
        for i in range(NUM_PIXELS):
            pixel_index = (i * 256 // NUM_PIXELS) + j
            pixels[i] = colorwheel(pixel_index & 255)
        pixels.show()
        time.sleep(speed)


def color_pulse():
    pixels.fill((COLOR_R, COLOR_G, COLOR_B))
    pixels.show()
        

def main():
  

  print("starting server..")
  # startup the server
  try:
    server.start(str(wifi.radio.ipv4_gateway_ap))
    print("Listening on http://%s:80" % wifi.radio.ipv4_gateway_ap)
  #  if the server fails to begin, restart the pico w
  except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()  
  
  while True:
    if LED_MODE == "rainbow":
        rainbow(RAINBOW_SPEED)
    elif LED_MODE == "color_pulse":
        color_pulse()
    #  poll the server for incoming/outgoing requests
    server.poll()

main()