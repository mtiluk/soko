import displayio
from adafruit_display_text import label
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.rect import Rect

from .. import theme
from ..model import hhmm, hhmm_long, TAXI_KT
from .base import Screen

NEAR_NM = 5


class FlightScreen(Screen):
    def build(self):
        self._logo_shown = None
        self._bar_fill = None

        self._logo_group = displayio.Group(
            scale=theme.LOGO_SCALE, x=theme.LOGO_X, y=theme.LOGO_Y
        )
        self.group.append(self._logo_group)

        text = displayio.Group(scale=theme.TEXT_SCALE)
        self._callsign = self._row(text, theme.TEXT_X, theme.ROW_1, theme.BRIGHT)
        self._route    = self._row(text, theme.TEXT_X, theme.ROW_2, theme.MID)
        self._actype   = self._row(text, theme.TEXT_X, theme.ROW_3, theme.DIM)
        self.group.append(text)

        status = displayio.Group()
        self._line1 = label.Label(theme.FONT, text="", color=theme.MID,
                                  x=theme.MARGIN_L, y=theme.ROW_4)
        self._line2 = label.Label(theme.FONT, text="", color=theme.MID,
                                  x=theme.MARGIN_L, y=theme.ROW_5)
        status.append(self._line1)
        status.append(self._line2)
        self.group.append(status)

        self._bar_group = displayio.Group()
        self._bar_group.append(
            Line(theme.MARGIN_L, theme.BAR_Y, theme.MARGIN_R, theme.BAR_Y, theme.FAINT)
        )
        self.group.append(self._bar_group)

    def _row(self, parent, x, y, colour):
        lbl = label.Label(theme.FONT, text="", color=colour,
                          x=x // theme.TEXT_SCALE, y=y // theme.TEXT_SCALE)
        parent.append(lbl)
        return lbl

    # --- logo ---------------------------------------------------------

    def _placeholder(self, text):
        box = displayio.Group()
        box.append(Rect(0, 0, theme.LOGO_W, theme.LOGO_H, outline=theme.FAINT))
        lbl = label.Label(theme.FONT, text=text[:3], color=theme.DIM)
        lbl.anchor_point = (0.5, 0.5)
        lbl.anchored_position = (theme.LOGO_W // 2, theme.LOGO_H // 2)
        box.append(lbl)
        return box

    def _logo(self, icao):
        if icao == self._logo_shown:
            return
        self._logo_shown = icao
        while len(self._logo_group):
            self._logo_group.pop()
        try:
            bmp = displayio.OnDiskBitmap("/logos/{}.bmp".format(icao))
            pal = bmp.pixel_shader
            pal.make_transparent(0)
            self._logo_group.append(displayio.TileGrid(bmp, pixel_shader=pal))
        except OSError:
            self._logo_group.append(self._placeholder(icao))

    # --- progress bar -------------------------------------------------

    def _set_progress(self, fraction):
        if self._bar_fill is not None:
            self._bar_group.remove(self._bar_fill)
            self._bar_fill = None
        fraction = min(max(fraction, 0.0), 1.0)
        end = theme.MARGIN_L + int((theme.MARGIN_R - theme.MARGIN_L) * fraction)
        if end > theme.MARGIN_L:
            self._bar_fill = Line(theme.MARGIN_L, theme.BAR_Y,
                                  end, theme.BAR_Y, theme.GREEN)
            self._bar_group.append(self._bar_fill)

    # --- status block -------------------------------------------------

    def _fit(self, lbl, text, limit=None):
        """Trim to the panel width, with an ellipsis if it overflows."""
        if limit is None:
            limit = theme.MARGIN_R - theme.MARGIN_L
        lbl.text = text
        while text and lbl.bounding_box[2] > limit:
            text = text[:-1]
            lbl.text = text + "..."

    def _status(self, line1, line2, colour=theme.MID):
        self._fit(self._line1, line1)
        self._fit(self._line2, line2)
        self._line1.color = self._line2.color = colour

    # --- update -------------------------------------------------------

    def update(self, state):
        """Called after a poll, not every frame."""
        self._logo(state.logo or state.callsign[:3])
        self._callsign.text = state.callsign
        self._callsign.color = theme.BRIGHT if state.fresh() else theme.MID
        self._route.text = state.route or "---"
        self._actype.text = state.actype or "----"

        legs = state.legs()
        gs = state.gs
        moving = bool(gs and gs > TAXI_KT)

        if legs is None:
            self._set_progress(0.0)
            if state.position is not None and state.fresh():
                alt = "{}ft".format(state.alt) if state.alt is not None else "--"
                spd = "{}kt".format(int(gs)) if gs else "--"
                self._status("In flight", alt + "  " + spd, theme.MID)
            else:
                self._status("Searching", "No route data", theme.DIM)
            return

        flown, left = legs

        if left < NEAR_NM and not moving:
            self._set_progress(1.0)
            elapsed = state.elapsed
            took = "Took " + hhmm_long(elapsed) if elapsed else "Flight complete"
            self._status(took, "Flight landed", theme.GREEN)
            return

        if flown < NEAR_NM and not moving:
            self._set_progress(0.0)
            self._status("On ground", "Preparing to takeoff", theme.MID)
            return

        self._set_progress(flown / (flown + left))

        if state.place:
            self._status("Flying over...", state.place, theme.MID)
        elif gs:
            self._status("Departed {} ago".format(hhmm(flown / gs)),
                         "Arriving in {}".format(hhmm(left / gs)), theme.MID)
        else:
            self._status("In flight", "{}nm to run".format(int(left)), theme.MID)
