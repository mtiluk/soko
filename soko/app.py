from soko.hardware import setup_hardware
from soko.screens.hello_world import draw_hello_world

def run():
    display = setup_hardware()

    draw_hello_world(display)

    while True:
        pass
