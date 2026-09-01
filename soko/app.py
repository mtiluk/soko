import time
from soko.hardware import setup_hardware
from soko.screens.hello_world import HelloWorld

FRAME_SLEEP = 0

def run():
    display = setup_hardware()
    screen = HelloWorld(display)

    last = time.monotonic()
    while True:
        now = time.monotonic()
        dt, last = now - last, now
        screen.tick(dt)
        time.sleep(FRAME_SLEEP)
