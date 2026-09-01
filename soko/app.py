import time
import displayio
from soko import theme
from soko.hardware import setup_hardware
from soko.screens.hello_world import HelloWorld
from soko.screens.loading import Loading
from soko.net import Net

def run():
    display = setup_hardware()

    root = displayio.Group()
    display.root_group = root

    screens = {"hello": HelloWorld(), "loading": Loading()}
    for screen in screens.values():
        root.append(screen.group)

    current = None

    def show(name):
        nonlocal current
        if current is not None:
            screens[current].group.hidden = True
        current = name
        screens[name].enter()
        screens[name].group.hidden = False

    show("loading")

    last = time.monotonic()
    switch_at = last + 5.0

    net = Net()
    net.connect()

    while True:
        now = time.monotonic()
        dt, last = now - last, now

        if now >= switch_at:
            switch_at = now + 5.0
            show("hello" if current == "loading" else "loading")

        screens[current].tick(dt)
        time.sleep(theme.FRAME_SLEEP)
