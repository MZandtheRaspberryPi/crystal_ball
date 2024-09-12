from adafruit_httpserver import Server, Request, Response, POST
import wifi
import socketpool

def bound_number(cur, min_bound, max_bound, increment):
    new_val = cur + increment
    if new_val > max_bound:
        new_val = max_bound
    if new_val < min_bound:
        new_val = min_bound
    return new_val

def setup_wifi(ssid_name: str, ssid_pass: str):
    wifi.radio.start_ap(ssid=ssid_name, password=ssid_pass)
    print("started network")
    pool = socketpool.SocketPool(wifi.radio)
    server = Server(pool, "/static")
    return server, pool