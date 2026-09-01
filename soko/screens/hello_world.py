import displayio
import terminalio
from adafruit_display_text import label

class HelloWorld:
    def __init__(self, display):
        self.number = 0

        self.label = label.Label(
            font=terminalio.FONT,
            text="0",
            color=0xE0E0E0,
        )
        self.label.anchor_point = (0.5, 0.5)
        self.label.anchored_position = (64, 32)

        root = displayio.Group()
        root.append(self.label)
        display.root_group = root

    def tick(self, dt):
        self.number += 1
        self.label.text = str(self.number)
