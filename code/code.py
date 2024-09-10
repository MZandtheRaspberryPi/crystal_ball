"""
Code to serve up a webserver that controls LEDs and toggles modes. Relies on some environment variables set in the settings.toml.
"""
import alarm
from analogio import AnalogIn
import digitalio
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
MODE_FORM_KEY = "mode"
MODE_RAINBOW = "rainbow_mode"
MODE_SLEEP = "sleep"
MODE_COLOR_PULSE = "color_pulse_mode"
RESET_VARS_FORM_KEY = "reset_variables"
SETTINGS_URL = "/settings"
RAINBOW_SETTINGS_URL = "/settings/rainbow"
COLOR_PULSE_SETTINGS_URL = "/settings/color_pulse"

TARGET_LOOP_RATE = 60 # hz
TARGET_LOOP_SECONDS = 1 / TARGET_LOOP_RATE
LAST_LOOP_TIME = time.time()
LED_MODE = MODE_RAINBOW
BRIGHTNESS = 0.5
BRIGHTNESS_LOWER_BOUND = 0.0
BRIGHTNESS_UPPER_BOUND = 1.0
BRIGHTNESS_FORM_KEY = "brightness"

RAINBOW_SPEED = 0
RAINBOW_MIN_SPEED = 0
RAINBOW_MAX_SPEED = 0.1
RAINBOW_SPEED_FORM_KEY = "rainbow_speed"
COLOR_R = 255
COLOR_R_FORM_KEY = "r"
COLOR_G = 0
COLOR_G_FORM_KEY = "g"
COLOR_B = 255
COLOR_B_FORM_KEY = "b"
COLOR_UPPER_BOUND = 255
COLOR_LOWER_BOUND = 0
#  font for HTML
FONT_FAMILY = "monospace"

BATTERY_LEVEL = 3.7

wifi.radio.start_ap(ssid=SSID_NAME, password=SSID_PASS)
print("started network")
pool = socketpool.SocketPool(wifi.radio)
server = Server(pool, "/static", debug=True)

# Update this to match the number of NeoPixel LEDs connected to your board.
ORDER = neopixel.RGB
PIXEL_PIN = board.D5
BUTTON_PIN = board.BUTTON
INBUILT_NEOPIXEL_PIN = board.NEOPIXEL_I2C_POWER
INBUILT_NEOPIXEL = digitalio.DigitalInOut(INBUILT_NEOPIXEL_PIN)
INBUILT_NEOPIXEL.direction = digitalio.Direction.OUTPUT
INBUILT_NEOPIXEL.value = False

pixels = neopixel.NeoPixel(
PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS, auto_write=False, pixel_order=ORDER)

BATTERY_PIN = board.VOLTAGE_MONITOR
BATTERY_IN = AnalogIn(BATTERY_PIN)
PIN_ALARM = alarm.pin.PinAlarm(pin=BUTTON_PIN, value=False)

def update_battery():
    global BATTERY_IN, BATTERY_LEVEL
    measured_voltage = BATTERY_IN.value
    # docs claim below, but it seems this isn't accurate
    # measured_voltage *= 2
    measured_voltage /= 1000
    BATTERY_LEVEL = measured_voltage


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
<h1>Current Settings</h1>
<div class="paragraph">
 <p class="dotted">Mode: <span style="color: deeppink;">{LED_MODE}</span></p>
</div>
<div class="paragraph">
 <p class="dotted">Battery: <span style="color: deeppink;">{BATTERY_LEVEL:.2f}</span></p>
</div>
<div class="paragraph">
	<p class="dotted">Brightness: <span style="color: deeppink;">{BRIGHTNESS:.2f}</span></p>
</div>
<div class="paragraph">
	<p class="dotted">Rainbow Speed: <span style="color: deeppink;">{RAINBOW_SPEED:.3f}</span></p>
</div>
<div class="paragraph">
	<p class="dotted">Red value: <span style="color: deeppink;">{COLOR_R}</span></p>
</div>
<div class="paragraph">
	<p class="dotted">Green value: <span style="color: deeppink;">{COLOR_G}</span></p>
</div>
<div class="paragraph">
	<p class="dotted">Blue value: <span style="color: deeppink;">{COLOR_B}</span></p>
</div>

<h1>Controls</h1>
<h2>General Controls</h2>
<p>
<form action="{SETTINGS_URL}" method="post" enctype="text/plain">
	<button class="button" name="{MODE_FORM_KEY}" value="{MODE_RAINBOW}" type="submit">Set Rainbow Mode</button>
</form>
</p>
<p>
<form action="{SETTINGS_URL}" method="post" enctype="text/plain">
	<button class="button" name="{MODE_FORM_KEY}" value="{MODE_COLOR_PULSE}" type="submit">Set Color Pulse Mode</button>
</form>
</p>
<p>
	<form action="{SETTINGS_URL}" method="post" enctype="text/plain">
		<button class="button" name="{MODE_FORM_KEY}" value="{MODE_SLEEP}" type="submit">Set Deep Sleep</button>
	</form>
</p>
<p>
<form action="{SETTINGS_URL}" method="post" enctype="text/plain">
	<input type="text" name="{BRIGHTNESS_FORM_KEY}" placeholder="Set brightness, {BRIGHTNESS_LOWER_BOUND} to {BRIGHTNESS_UPPER_BOUND}.">
	<input type="submit" value="Submit">
</form>
</p>
<p>
<form action="{SETTINGS_URL}" method="post" enctype="text/plain">
	<button class="button" name="{RESET_VARS_FORM_KEY}" value="yes" type="submit">Reset Variables</button>
</form>
</p>
<h2>Rainbow Controls</h2>
<p>
<form action="{RAINBOW_SETTINGS_URL}" method="post" enctype="text/plain">
	<input type="text" name="{RAINBOW_SPEED_FORM_KEY}" placeholder="Set rainbow speed, {RAINBOW_MIN_SPEED} to {RAINBOW_MAX_SPEED}.">
	<input type="submit" value="Submit">
</form>
</p>
<h2>Color Pulse Controls</h3>
<p>
<form action="{COLOR_PULSE_SETTINGS_URL}" method="post" enctype="text/plain">
	<input type="text" name="{COLOR_R_FORM_KEY}" placeholder="Set red value, {COLOR_LOWER_BOUND} to {COLOR_UPPER_BOUND}.">
	<input type="submit" value="Submit">
</form>
</p>
<p>
<form action="{COLOR_PULSE_SETTINGS_URL}" method="post" enctype="text/plain">
	<input type="text" name="{COLOR_G_FORM_KEY}" placeholder="Set green value, {COLOR_LOWER_BOUND} to {COLOR_UPPER_BOUND}.">
	<input type="submit" value="Submit">
</form>
</p>
<p>
<form action="{COLOR_PULSE_SETTINGS_URL}" method="post" enctype="text/plain">
	<input type="text" name="{COLOR_B_FORM_KEY}" placeholder="Set blue value, {COLOR_LOWER_BOUND} to {COLOR_UPPER_BOUND}.">
	<input type="submit" value="Submit">
</form>
</p>
</body></html>
"""
  return html


def bound_number(cur, min_bound, max_bound, increment):
    new_val = cur + increment
    if new_val > max_bound:
        new_val = max_bound
    if new_val < min_bound:
        new_val = min_bound
    return new_val

@server.route(SETTINGS_URL, [POST])
def settings(request: Request):

    brightness_req = request.form_data.get(BRIGHTNESS_FORM_KEY, None)
    if not brightness_req is None:
        global BRIGHTNESS
        brightness = BRIGHTNESS
        try:
            brightness = float(brightness_req.strip())
        except ValueError:
            pass
        BRIGHTNESS = bound_number(brightness, BRIGHTNESS_LOWER_BOUND, BRIGHTNESS_UPPER_BOUND, 0)
        pixels.brightness = BRIGHTNESS

    mode = request.form_data.get(MODE_FORM_KEY, None)
    if not mode is None:
        mode = mode.strip()
        global LED_MODE
        if mode == MODE_RAINBOW:
            LED_MODE = MODE_RAINBOW
        elif mode == MODE_COLOR_PULSE:
            LED_MODE = MODE_COLOR_PULSE
        elif mode == MODE_SLEEP:
            global server
            server.stop()
            wifi.radio.stop_ap()
            pixels.fill((0, 0, 0))
            pixels.show()
            alarm.exit_and_deep_sleep_until_alarms(PIN_ALARM)
        else:
            pass
    
    reset_vars = request.form_data.get(RESET_VARS_FORM_KEY, None)
    if not reset_vars is None:
        global LED_MODE, BRIGHTNESS, RAINBOW_SPEED, COLOR_R, COLOR_B, COLOR_G
        LED_MODE = MODE_RAINBOW
        BRIGHTNESS = 0.5
        RAINBOW_SPEED = 0
        COLOR_R = 255
        COLOR_G = 0
        COLOR_B = 255
    return Response(request, f"{web_page()}", content_type='text/html')


@server.route(RAINBOW_SETTINGS_URL, [POST])
def settings_rainbow(request: Request):

    rainbow_speed = request.form_data.get(RAINBOW_SPEED_FORM_KEY, None)
    if not rainbow_speed is None:
        global RAINBOW_SPEED
        speed = RAINBOW_SPEED
        try:
            speed = float(rainbow_speed.strip())
        except ValueError:
            pass
        RAINBOW_SPEED = bound_number(speed, RAINBOW_MIN_SPEED, RAINBOW_MAX_SPEED, 0)
    return Response(request, f"{web_page()}", content_type='text/html')


@server.route(COLOR_PULSE_SETTINGS_URL, [POST])
def settings_color_pulse(request: Request):

    r_val = request.form_data.get(COLOR_R_FORM_KEY, None)
    if not r_val is None:
        global COLOR_R
        r = COLOR_R
        try:
            r = int(r_val.strip())
        except ValueError:
            pass
        COLOR_R = bound_number(r, COLOR_LOWER_BOUND, COLOR_UPPER_BOUND, 0)
    
    g_val = request.form_data.get(COLOR_G_FORM_KEY, None)
    if not g_val is None:
        global COLOR_G
        g = COLOR_G
        try:
            g = int(g_val.strip())
        except ValueError:
            pass
        COLOR_G = bound_number(g, COLOR_LOWER_BOUND, COLOR_UPPER_BOUND, 0)
    
    b_val = request.form_data.get(COLOR_B_FORM_KEY, None)
    if not b_val is None:
        global COLOR_B
        b = COLOR_B
        try:
            b = int(b_val.strip())
        except ValueError:
            pass
        COLOR_B = bound_number(b, COLOR_LOWER_BOUND, COLOR_UPPER_BOUND, 0)

    return Response(request, f"{web_page()}", content_type='text/html')

#  route default static IP
@server.route("/")
def base(request: Request):  # pylint: disable=unused-argument
    #  serve the HTML f string
    #  with content type text/html
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
  global LAST_LOOP_TIME, TARGET_LOOP_SECONDS
  while True:
    seconds_before_loop = (time.time() - LAST_LOOP_TIME) - TARGET_LOOP_SECONDS
    if seconds_before_loop < 0:
        time.sleep(abs(seconds_before_loop))
    LAST_LOOP_TIME = time.time()

    if LED_MODE == MODE_RAINBOW:
        rainbow(RAINBOW_SPEED)
    elif LED_MODE == MODE_COLOR_PULSE:
        color_pulse()
    #  poll the server for incoming/outgoing requests
    server.poll()
    update_battery()

main()