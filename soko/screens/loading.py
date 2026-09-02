import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_text import label

from .. import theme
from .base import Screen

BEACON = 0x800000
BEACON_PERIOD = 1.4
BEACON_ON = 0.12


class Loading(Screen):
    def build(self):
        g = self.group

        g.append(Triangle(48, 36, 70, 36, 62, 50, fill=theme.DIM))
        g.append(Triangle(48, 36, 62, 50, 50, 50, fill=theme.DIM))

        g.append(RoundRect(50, 43, 16, 6, 3, fill=theme.MID))

        g.append(Triangle(86, 28, 98, 12, 106, 12, fill=theme.BRIGHT))
        g.append(Triangle(86, 28, 106, 12, 104, 28, fill=theme.BRIGHT))

        g.append(RoundRect(18, 27, 86, 11, 5, fill=theme.MID))

        g.append(Rect(22, 29, 6, 2, fill=theme.FAINT))

        windows = displayio.Bitmap(60, 1, 2)
        pal = displayio.Palette(2)
        pal[0] = 0x000000
        pal[1] = theme.FAINT
        pal.make_transparent(0)
        for x in range(0, 60, 5):
            windows[x, 0] = 1
        g.append(displayio.TileGrid(windows, pixel_shader=pal, x=34, y=31))

        self._beacon = Rect(101, 10, 2, 2, fill=BEACON)
        g.append(self._beacon)
        tag = label.Label(theme.FONT, text="loading", color=theme.FAINT)
        tag.anchor_point = (1.0, 1.0)
        tag.anchored_position = (theme.MARGIN_R, theme.HEIGHT - 2)
        g.append(tag)
        self._t = 0.0

    def enter(self):
        self._t = 0.0

    def tick(self, dt):
        self._t += dt
        self._beacon.hidden = (self._t % BEACON_PERIOD) > BEACON_ON
