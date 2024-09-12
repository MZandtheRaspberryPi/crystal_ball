from adafruit_httpserver import Route, POST, GET, Request, Response
import alarm
from analogio import AnalogIn
import digitalio
import time
import board
import microcontroller
from rainbowio import colorwheel
import neopixel
import wifi



from constants import (PIXEL_PIN,
                       BUTTON_PIN,
                       INBUILT_NEOPIXEL_PIN,
                       BATTERY_PIN,
                       SSID_NAME,
                       SSID_PASS,
                       NUM_PIXELS,
                       MODE_FORM_KEY,
                       MODE_RAINBOW,
                       MODE_SLEEP,
                       MODE_COLOR_PULSE,
                       RESET_VARS_FORM_KEY,
                       SETTINGS_URL,
                       RAINBOW_SETTINGS_URL,
                       COLOR_PULSE_SETTINGS_URL,
                       TARGET_LOOP_RATE,
                       TARGET_LOOP_SECONDS,
                       BRIGHTNESS_LOWER_BOUND,
                       BRIGHTNESS_UPPER_BOUND,
                       BRIGHTNESS_FORM_KEY,
                       RAINBOW_MIN_SPEED,
                       RAINBOW_MAX_SPEED,
                       RAINBOW_SPEED_FORM_KEY,
                       COLOR_R_FORM_KEY,
                       COLOR_G_FORM_KEY,
                       COLOR_B_FORM_KEY,
                       COLOR_UPPER_BOUND,
                       COLOR_LOWER_BOUND,
                       ORDER)
from util import setup_wifi, bound_number


class CrystalBall:
    def __init__(self):
        server, pool = setup_wifi(SSID_NAME, SSID_PASS)
        self.server = server
        self.pool = pool
        
        self.led_mode = MODE_RAINBOW
        self.brightness = 0.5
        self.rainbow_speed = 0
        self.color_r = 255
        self.color_g = 0
        self.color_b = 255
        self.battery_level = -1

        self.inbuilt_neopixel = digitalio.DigitalInOut(INBUILT_NEOPIXEL_PIN)
        self.inbuilt_neopixel.direction = digitalio.Direction.OUTPUT
        self.inbuilt_neopixel.value = False

        self.pixels = neopixel.NeoPixel(
                PIXEL_PIN, NUM_PIXELS,
                brightness=self.brightness, auto_write=False, pixel_order=ORDER)
        
        self.battery_in = AnalogIn(BATTERY_PIN)
        self.pin_alarm = alarm.pin.PinAlarm(pin=BUTTON_PIN, value=False)

        self.server.add_routes([
            Route(SETTINGS_URL, [POST], self.settings),
            Route(RAINBOW_SETTINGS_URL, [POST], self.settings_rainbow),
            Route(COLOR_PULSE_SETTINGS_URL, [POST], self.settings_color_pulse),
            Route("/", [GET], self.base)
        ])

        print("starting server..")
        # startup the server
        try:
            self.server.start(str(wifi.radio.ipv4_gateway_ap))
            print("Listening on http://%s" % wifi.radio.ipv4_gateway_ap)
            #  if the server fails to begin, restart the pico w
        except OSError:
            time.sleep(5)
            print("restarting..")
            microcontroller.reset()  
    
    def get_mode(self):
        return self.led_mode

    def measure_battery(self):
        measured_adc = self.battery_in.value
        measured_voltage = measured_adc * 3.3 * 2 / 65536
        self.battery_level = measured_voltage
    
    def poll_server(self):
        #  poll the server for incoming/outgoing requests
        self.server.poll()
    
    def get_webpage(self):

        LED_MODE = self.led_mode
        BRIGHTNESS = self.brightness
        RAINBOW_SPEED = self.rainbow_speed
        COLOR_R = self.color_r
        COLOR_G = self.color_g
        COLOR_B = self.color_b
        BATTERY_LEVEL = self.battery_level

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta http-equiv="Content-type" content="text/html;charset=utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
html{{font-family: monospace; background-color: lightgrey;
display:block; margin: 0px auto; text-align: center;}}
    h1{{color: deeppink; padding: 2vh; font-size: 2rem;}}
    h2{{color: deeppink; padding: 2vh; font-size: 1.75rem;}}
    p{{font-size: 1.5rem; display: block;}}
    .button{{font-family: monospace; display: inline-block;
    background-color: black; border: none;
    border-radius: 4px; color: white; padding: 1rem 2.5rem;
    text-decoration: none; font-size: 1.5rem; margin: 2px; cursor: pointer;}}
    p.dotted {{margin: auto; display: block;
    text-align: center;}}
    .input{{font-family: monospace; display: inline-block;
    background-color: black; border: none;
    border-radius: 4px; color: white; padding: 1rem 2.5rem;
    text-decoration: none; font-size: 1rem; margin: 2px; cursor: pointer;}}
    .submit{{font-family: monospace; display: inline-block;
    background-color: black; border: none;
    border-radius: 4px; color: white; padding: 1rem 2.5rem;
    text-decoration: none; font-size: 1rem; margin: 2px; cursor: pointer;}}
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
    <p class="dotted">Blue value: <span style="color: #ff1493;">{COLOR_B}</span></p>
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
    <input class="input" type="text" name="{BRIGHTNESS_FORM_KEY}" placeholder="Brightness: {BRIGHTNESS_LOWER_BOUND}-{BRIGHTNESS_UPPER_BOUND}">
    <input class="submit" type="submit" value="Submit">
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
    <input class="input" type="text" name="{RAINBOW_SPEED_FORM_KEY}" placeholder="Rainbow speed: {RAINBOW_MIN_SPEED}-{RAINBOW_MAX_SPEED}">
    <input class="submit" type="submit" value="Submit">
</form>
</p>
<h2>Color Pulse Controls</h3>
<p>
<form action="{COLOR_PULSE_SETTINGS_URL}" method="post" enctype="text/plain">
    <p>
        <input class="input" type="text" name="{COLOR_R_FORM_KEY}" placeholder="Red: {COLOR_LOWER_BOUND}-{COLOR_UPPER_BOUND}">
    </p>
    <p>
        <input class="input" type="text" name="{COLOR_G_FORM_KEY}" placeholder="Green: {COLOR_LOWER_BOUND}-{COLOR_UPPER_BOUND}">
    </p>
    <p>
        <input class="input" type="text" name="{COLOR_B_FORM_KEY}" placeholder="Blue: {COLOR_LOWER_BOUND}-{COLOR_UPPER_BOUND}">
    </p>
    <input class="submit" type="submit" value="Submit">
</form>
</p>
</body></html>
"""
        return html

    def settings(self, request: Request):

        brightness_req = request.form_data.get(BRIGHTNESS_FORM_KEY, None)
        if not brightness_req is None:
            brightness = self.brightness
            try:
                brightness = float(brightness_req.strip())
            except ValueError:
                pass
            self.brightness = bound_number(brightness, BRIGHTNESS_LOWER_BOUND, BRIGHTNESS_UPPER_BOUND, 0)
            self.pixels.brightness = self.brightness

        mode = request.form_data.get(MODE_FORM_KEY, None)
        if not mode is None:
            mode = mode.strip()
            if mode == MODE_RAINBOW:
                self.led_mode = MODE_RAINBOW
            elif mode == MODE_COLOR_PULSE:
                self.led_mode = MODE_COLOR_PULSE
            elif mode == MODE_SLEEP:
                self.server.stop()
                wifi.radio.stop_ap()
                self.pixels.fill((0, 0, 0))
                self.pixels.show()
                alarm.exit_and_deep_sleep_until_alarms(self.pin_alarm)
            else:
                pass
        
        reset_vars = request.form_data.get(RESET_VARS_FORM_KEY, None)
        if not reset_vars is None:
            self.led_mode = MODE_RAINBOW
            self.brightness = 0.5
            self.rainbow_speed = 0
            self.color_r = 255
            self.color_g = 0
            self.color_b = 255
        return Response(request, f"{self.get_webpage()}", content_type='text/html')


    def settings_rainbow(self, request: Request):

        rainbow_speed = request.form_data.get(RAINBOW_SPEED_FORM_KEY, None)
        if not rainbow_speed is None:
            speed = self.rainbow_speed
            try:
                speed = float(rainbow_speed.strip())
            except ValueError:
                pass
            self.rainbow_speed = bound_number(speed, RAINBOW_MIN_SPEED, RAINBOW_MAX_SPEED, 0)
        return Response(request, f"{self.get_webpage()}", content_type='text/html')

    def settings_color_pulse(self, request: Request):

        r_val = request.form_data.get(COLOR_R_FORM_KEY, None)
        if not r_val is None:
            r = self.color_r
            try:
                r = int(r_val.strip())
            except ValueError:
                pass
            self.color_r = bound_number(r, COLOR_LOWER_BOUND, COLOR_UPPER_BOUND, 0)
        
        g_val = request.form_data.get(COLOR_G_FORM_KEY, None)
        if not g_val is None:
            g = self.color_g
            try:
                g = int(g_val.strip())
            except ValueError:
                pass
            self.color_g = bound_number(g, COLOR_LOWER_BOUND, COLOR_UPPER_BOUND, 0)
        
        b_val = request.form_data.get(COLOR_B_FORM_KEY, None)
        if not b_val is None:
            b = self.color_b
            try:
                b = int(b_val.strip())
            except ValueError:
                pass
            self.color_b = bound_number(b, COLOR_LOWER_BOUND, COLOR_UPPER_BOUND, 0)

        return Response(request, f"{self.get_webpage()}", content_type='text/html')

    def base(self, request: Request):  # pylint: disable=unused-argument
        #  serve the HTML f string
        #  with content type text/html
        return Response(request, f"{self.get_webpage()}", content_type='text/html')


    def rainbow(self):
        for j in range(255):
            for i in range(NUM_PIXELS):
                pixel_index = (i * 256 // NUM_PIXELS) + j
                self.pixels[i] = colorwheel(pixel_index & 255)
            self.pixels.show()
            time.sleep(self.rainbow_speed)

    def color_pulse(self):
        self.pixels.fill((self.color_r, self.color_g, self.color_b))
        self.pixels.show()