import terminalio
from adafruit_display_text import label
from .. import theme
from .base import Screen


class HelloWorld(Screen):
    def build(self):
        self.number = 0

        self.label = label.Label(
            font=terminalio.FONT,
            text="0",
            color=theme.BRIGHT,
        )
        self.label.anchor_point = (0.5, 0.5)
        self.label.anchored_position = (theme.WIDTH // 2, theme.HEIGHT // 2)

        self.group.append(self.label)

    def enter(self):
        self.number = 0

    def tick(self, dt):
        self.number += 1
        self.label.text = str(self.number)
