import os
import time
import displayio

from soko import theme
from soko.api import FlightAPI
from soko.hardware import setup_hardware
from soko.model import FlightState, RadarState
from soko.net import Net
from soko.screens.flight import FlightScreen
from soko.screens.loading import Loading
from soko.screens.radar import RadarScreen

CALLSIGN = os.getenv("CALLSIGN")
MODE = (os.getenv("MODE") or ("flight" if CALLSIGN else "radar")).lower()
HOME = (float(os.getenv("HOME_LAT") or 0), float(os.getenv("HOME_LON") or 0))
RADAR_NM = min(int(os.getenv("RADAR_NM") or 25), 250)   # adsb.lol caps at 250
POLL_SECONDS = 15
ROTATE_SECONDS = 10
RADAR_TRIES = 4


def run():
    display = setup_hardware()
    root = displayio.Group()
    display.root_group = root

    screens = {
        "loading": Loading(),
        "flight": FlightScreen(),
        "radar": RadarScreen(),
    }
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
    print("app: connected, mode =", MODE)

    api = FlightAPI(net)
    state = FlightState(CALLSIGN)
    radar = RadarState(HOME, RADAR_NM, hold_seconds=ROTATE_SECONDS)

    def radar_advance():
        picked = None
        for _ in range(RADAR_TRIES):
            picked = radar.choose()
            if picked is None:
                break
            if not picked.route and not picked.route_missing:
                api.fetch_route(picked)
                radar.remember_route(picked)
            if picked.route:
                break
            radar.skip()
        if picked is not None and radar.current is None:
            radar.current = picked
            radar.since = time.monotonic()
        screens["radar"].update(radar)

    last = time.monotonic()
    last_poll = 0.0

    while True:
        now = time.monotonic()
        dt, last = now - last, now

        if now - last_poll >= POLL_SECONDS:
            last_poll = now
            if MODE == "radar":
                radar.update_list(api.fetch_nearby(HOME[0], HOME[1], RADAR_NM))
            else:
                api.fetch_position(state)
                state.note_movement()
                api.fetch_route(state)
                screens["flight"].update(state)

        if MODE == "radar":
            if radar.due():
                radar_advance()
            show("radar" if radar.current else "loading")
        else:
            show("flight" if state.have_anything() else "loading")

        screens[current].tick(dt)
        time.sleep(theme.FRAME_SLEEP)
