import os
import time

import displayio
from soko import theme
from soko.api import FlightAPI
from soko.hardware import setup_hardware
from soko.model import FlightState
from soko.net import Net
from soko.screens.flight import FlightScreen
from soko.screens.loading import Loading

CALLSIGN = os.getenv("CALLSIGN")
POLL_SECONDS = 15

def run():
    display = setup_hardware()

    root = displayio.Group()
    display.root_group = root

    screens = {"loading": Loading(), "flight": FlightScreen()}
    for screen in screens.values():
        root.append(screen.group)

    current = None

    def show(name):
        nonlocal current
        if name == current:
            return
        if current is not None:
            screens[current].group.hidden = True
        current = name
        screens[name].enter()
        screens[name].group.hidden = False

    show("loading")

    net = Net()
    net.connect()

    print("app: connected, callsign =", CALLSIGN)
    state = FlightState(CALLSIGN)
    api = FlightAPI(net)

    last = time.monotonic()
    last_poll = 0.0

    while True:
        now = time.monotonic()
        dt, last = now - last, now

        if now - last_poll >= POLL_SECONDS:
            last_poll = now
            api.fetch_position(state)
            api.fetch_route(state)
            screens["flight"].update(state)

        show("flight" if state.have_anything() else "loading")

        screens[current].tick(dt)
        time.sleep(theme.FRAME_SLEEP)
