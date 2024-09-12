"""
Code to serve up a webserver that controls LEDs and toggles modes. Relies on some environment variables set in the settings.toml.
"""
import time

from constants import TARGET_LOOP_SECONDS, MODE_RAINBOW, MODE_COLOR_PULSE
from crystal_ball import CrystalBall

       

def main():
    crystal_ball = CrystalBall()
    last_loop_time = time.monotonic()
    while True:
        start_time = time.monotonic()
        seconds_before_loop = (start_time - last_loop_time) - TARGET_LOOP_SECONDS
        if seconds_before_loop < 0:
            time.sleep(abs(seconds_before_loop))
        last_loop_time = time.monotonic()

        mode = crystal_ball.get_mode()
        if mode == MODE_RAINBOW:
            crystal_ball.rainbow()
        elif mode == MODE_COLOR_PULSE:
            crystal_ball.color_pulse()
        else:
            pass
        crystal_ball.measure_battery()
        crystal_ball.poll_server()

main()
