import os
import ssl
import socketpool
import adafruit_requests
import wifi

class Net:
    def __init__(self):
        self.pool = None
        self.session = None

    def connect(self):
        wifi.radio.connect(os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD"))
        self.pool = socketpool.SocketPool(wifi.radio)
        self.session = adafruit_requests.Session(self.pool, ssl.create_default_context())
        print("net: connected as", wifi.radio.ipv4_address)
