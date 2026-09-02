from adafruit_display_text import label

from .. import theme
from ..model import compass, thousands
from .flight import FlightScreen


class RadarScreen(FlightScreen):
    """Same layout as the flight screen, minus the bar, plus a range readout."""

    def build(self):
        super().build()
        self._bar_group.hidden = True

        self._range = label.Label(theme.FONT, text="", color=theme.DIM)
        self._range.anchor_point = (1.0, 0.5)
        self._range.anchored_position = (theme.MARGIN_R, theme.ROW_4)
        self.group.append(self._range)

    def _telemetry(self, state):
        """'36,000ft  440kt', with dashes for whatever's missing."""
        alt = thousands(state.alt) + "ft" if state.alt is not None else "--"
        spd = "{}kt".format(int(state.gs)) if state.gs else "--"
        return alt + "  " + spd

    def update(self, radar):
        state = radar.current
        if state is None:
            self._logo("")
            self._callsign.text = "RADAR"
            self._callsign.color = theme.MID
            self._route.text = "---"
            self._actype.text = "----"
            self._range.text = ""
            self._status("Scanning", "{}nm radius".format(radar.radius_nm), theme.DIM)
            return

        self._logo(state.logo or state.callsign[:3])
        self._callsign.text = state.callsign
        self._callsign.color = theme.BRIGHT
        self._actype.text = state.actype or "----"

        rng = radar.range_of(state)
        self._range.text = "{}nm {}".format(int(rng[0]), rng[1]) if rng else ""

        if state.route:
            self._route.text = state.route
            self._status("From " + (state.orig_name or "?"),
                         "To " + (state.dest_name or "?"), theme.MID)
        else:
            self._route.text = state.reg or "---"
            heading = ("Heading " + compass(state.track)
                       if state.track is not None else "In flight")
            self._status(heading, self._telemetry(state), theme.MID)

        self._fit(self._line1, self._line1.text,
                  theme.MARGIN_R - theme.MARGIN_L - self._range.bounding_box[2] - 4)
