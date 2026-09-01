import math
import displayio

from .. import theme
from .base import Screen

COLS, ROWS = 7, 4
CELL = 5
GRID_Y = (theme.HEIGHT - ROWS * CELL) // 2

WAVE_SPEED = 2.6
WAVE_PITCH = 0.55

SHADES = (theme.FAINT, theme.DIM, theme.MID, theme.BRIGHT)

class Loading(Screen):
    def build(self):
        self._t = 0.0

        self._bitmap = displayio.Bitmap(COLS, ROWS, len(SHADES))
        palette = displayio.Palette(len(SHADES))
        for i, colour in enumerate(SHADES):
            palette[i] = colour

        grid = displayio.Group(
            scale=CELL,
            x=(theme.WIDTH - COLS * CELL) // 2,
            y=GRID_Y,
        )
        grid.append(displayio.TileGrid(self._bitmap, pixel_shader=palette))
        self.group.append(grid)

    def enter(self):
        self._t = 0.0

    def tick(self, dt):
        self._t += dt * WAVE_SPEED

        for y in range(ROWS):
            for x in range(COLS):
                wave = math.sin(self._t - (x + y) * WAVE_PITCH)
                level = int((wave + 1.0) * 0.5 * (len(SHADES) - 1) + 0.5)
                self._bitmap[x, y] = level
