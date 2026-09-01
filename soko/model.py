import math
import time

EARTH_RADIUS_NM = 3440.065

def distance_nm(a, b):
    """Great-circle distance between two (lat, lon) pairs."""
    lat1, lon1, lat2, lon2 = [math.radians(v) for v in (a[0], a[1], b[0], b[1])]
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * EARTH_RADIUS_NM * math.asin(math.sqrt(h))


def hhmm(hours):
    """Format a duration as '2h05' or '43m'."""
    if hours < 0:
        hours = 0
    h, m = int(hours), int(hours % 1 * 60)
    return "{}h{:02d}".format(h, m) if h else "{}m".format(m)


class FlightState:
    def __init__(self, callsign, stale_after=300):
        self.stale_after = stale_after
        self.reset(callsign)

    def reset(self, callsign):
        self.callsign = (callsign or "").upper()
        self.actype = ""
        self.lat = None
        self.lon = None
        self.gs = None
        self.alt = None
        self.route = ""
        self.orig = None            # (lat, lon)
        self.dest = None
        self.route_missing = False
        self.last_seen = None

    @property
    def position(self):
        return None if self.lat is None else (self.lat, self.lon)

    def fresh(self):
        return (self.last_seen is not None
                and time.monotonic() - self.last_seen < self.stale_after)

    def have_anything(self):
        return self.last_seen is not None or bool(self.route)

    def legs(self):
        """(flown_nm, remaining_nm), or None if route or position is missing."""
        if self.position is None or self.orig is None:
            return None
        return (distance_nm(self.orig, self.position),
                distance_nm(self.position, self.dest))

    def progress(self):
        legs = self.legs()
        if legs is None:
            return None
        total = legs[0] + legs[1]
        return 0.0 if total <= 0 else min(max(legs[0] / total, 0.0), 1.0)
