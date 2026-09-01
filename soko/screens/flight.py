import displayio
import terminalio
from adafruit_display_text import label

from .. import theme
from .base import Screen

ROW_1, ROW_2, ROW_3 = 14, 30, 46

class FlightScreen(Screen):
    def build(self):
        self._callsign = self._row(ROW_1, theme.BRIGHT)
        self._route = self._row(ROW_2, theme.MID)
        self._actype = self._row(ROW_3, theme.DIM)

    def _row(self, y, colour):
        lbl = label.Label(terminalio.FONT, text="", color=colour)
        lbl.anchor_point = (0.5, 0.5)
        lbl.anchored_position = (theme.WIDTH // 2, y)
        self.group.append(lbl)
        return lbl

    def update(self, state):
        """Called after a poll, not every frame."""
        self._callsign.text = state.callsign
        self._callsign.color = theme.BRIGHT if state.fresh() else theme.MID
        self._route.text = state.route or "---"
        self._actype.text = state.actype or "----"
