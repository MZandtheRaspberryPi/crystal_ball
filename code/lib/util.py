from adafruit_httpserver import Server, Request, Response, POST
import ipaddress
import wifi
import time
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
    print(f"ap active: {wifi.radio.ap_active}")
    wifi.radio.set_ipv4_address_ap(ipv4=ipaddress.IPv4Address("10.42.0.1"), netmask=ipaddress.IPv4Address("255.255.255.0"), gateway=ipaddress.IPv4Address("10.42.0.1"))
    wifi.radio.start_dhcp_ap()
    print(f"gateway: {wifi.radio.ipv4_gateway_ap}")
    pool = socketpool.SocketPool(wifi.radio)
    server = Server(pool, "/static")
    return server, pool


