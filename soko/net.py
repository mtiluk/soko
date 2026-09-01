import os
import ssl
import socketpool
import adafruit_requests
import wifi
import gc

HEADERS = {
    "User-Agent": "Mozilla/5.0 Soko/1.0",
    "Accept": "application/json",
}


class Net:
    def __init__(self):
        self.pool = None
        self.session = None

    def connect(self):
        wifi.radio.connect(os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD"))
        self._build_session()
        print("net: connected as", wifi.radio.ipv4_address)

    def _build_session(self):
        self.pool = socketpool.SocketPool(wifi.radio)
        self.session = adafruit_requests.Session(self.pool, ssl.create_default_context())

    def get_json(self, url):
        gc.collect()
        response = None
        try:
            response = self.session.get(url, timeout=10, headers=HEADERS)
            code = response.status_code
            return (response.json() if code == 200 else None), code
        except Exception as err:
            print("net: GET failed:", err)
            self._build_session()
            return None, 0
        finally:
            if response is not None:
                response.close()
