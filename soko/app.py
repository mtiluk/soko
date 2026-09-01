import time
import displayio
from soko.hardware import setup_hardware
from soko.screens.hello_world import HelloWorld
import soko.theme as theme

def run():
    display = setup_hardware()

    root = displayio.Group()
    display.root_group = root

    screens = {"hello": HelloWorld()}
    for screen in screens.values():
        root.append(screen.group)

    current = screens["hello"]
    current.group.hidden = False
    current.enter()

    last = time.monotonic()
    while True:
        now = time.monotonic()
        dt, last = now - last, now
        current.tick(dt)
        time.sleep(theme.FRAME_SLEEP)
