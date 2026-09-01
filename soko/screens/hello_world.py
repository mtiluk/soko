import displayio
import terminalio
from adafruit_display_text import label


def draw_hello_world(display):
    root = displayio.Group()

    text_area = label.Label(
        font=terminalio.FONT,
        text="Hello, World!",
        color=0xE0E0E0,
    )
    text_area.anchor_point = (0.5, 0.5)
    text_area.anchored_position = (64, 32)

    root.append(text_area)
    display.root_group = root
