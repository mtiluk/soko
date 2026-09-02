import math
import time

EARTH_RADIUS_NM = 3440.065
TAXI_KT = 40


def distance_nm(a, b):
    """Great-circle distance between two (lat, lon) pairs."""
    lat1, lon1, lat2, lon2 = [math.radians(v) for v in (a[0], a[1], b[0], b[1])]
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * EARTH_RADIUS_NM * math.asin(math.sqrt(h))


def bearing_deg(a, b):
    """Initial bearing from a to b, 0-360."""
    lat1, lon1, lat2, lon2 = [math.radians(v) for v in (a[0], a[1], b[0], b[1])]
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = (math.cos(lat1) * math.sin(lat2)
         - math.sin(lat1) * math.cos(lat2) * math.cos(dlon))
    return (math.degrees(math.atan2(x, y)) + 360) % 360


def compass(deg):
    points = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
    return points[int((deg + 22.5) // 45) % 8]


def hhmm(hours):
    """Format a duration as '2h05' or '43m'."""
    if hours < 0:
        hours = 0
    h, m = int(hours), int(hours % 1 * 60)
    return "{}h{:02d}".format(h, m) if h else "{}m".format(m)


def hhmm_long(hours):
    """Format a duration as '4h 20min' or '43min'."""
    if hours < 0:
        hours = 0
    h, m = int(hours), int(hours % 1 * 60)
    return "{}h {}min".format(h, m) if h else "{}min".format(m)


def thousands(n):
    """36000 -> '36,000'. CircuitPython's format() has no ',' option."""
    s = str(int(n))
    out = ""
    while len(s) > 3:
        out = "," + s[-3:] + out
        s = s[:-3]
    return s + out


def _num(v):
    return v if isinstance(v, (int, float)) else None


def _callsign_of(a):
    return (a.get("flight") or "").strip().upper()


def _looks_airline(cs):
    """ICAO airline callsigns are three letters then a flight number."""
    return len(cs) >= 4 and cs[:3].isalpha() and cs[3].isdigit()


class FlightState:
    def __init__(self, callsign, stale_after=300):
        self.stale_after = stale_after
        self.reset(callsign)

    def reset(self, callsign):
        self.callsign = (callsign or "").upper()
        self.actype = ""
        self.reg = ""
        self.logo = ""
        self.lat = None
        self.lon = None
        self.gs = None
        self.alt = None
        self.track = None
        self.route = ""
        self.orig = None
        self.dest = None
        self.orig_name = ""
        self.dest_name = ""
        self.route_missing = False
        self.last_seen = None
        self.place = ""
        self.place_at = None
        self.departed_at = None

    def apply_aircraft(self, a):
        """Hydrate from a raw adsb.lol record."""
        self.actype = a.get("t") or self.actype
        self.reg = (a.get("r") or self.reg).strip()
        self.lat = a.get("lat")
        self.lon = a.get("lon")
        self.gs = _num(a.get("gs"))
        self.alt = _num(a.get("alt_baro"))
        self.track = _num(a.get("track"))
        self.last_seen = time.monotonic()

    @property
    def position(self):
        return None if self.lat is None else (self.lat, self.lon)

    def fresh(self):
        return (self.last_seen is not None
                and time.monotonic() - self.last_seen < self.stale_after)

    def have_anything(self):
        return self.last_seen is not None or bool(self.route)

    def note_movement(self):
        """Start the clock the first time the aircraft is seen airborne."""
        if self.gs and self.gs > TAXI_KT and self.departed_at is None:
            self.departed_at = time.monotonic()

    @property
    def elapsed(self):
        """Hours since we first saw it moving, or None. Resets on reboot."""
        if self.departed_at is None:
            return None
        return (time.monotonic() - self.departed_at) / 3600.0

    def needs_place(self, min_move_nm=20):
        """True when the position has drifted far enough to re-geocode."""
        if self.position is None:
            return False
        if self.place_at is None:
            return True
        return distance_nm(self.place_at, self.position) > min_move_nm

    def legs(self):
        """(flown_nm, remaining_nm), or None if route or position is missing."""
        if self.position is None or self.orig is None or self.dest is None:
            return None
        return (distance_nm(self.orig, self.position),
                distance_nm(self.position, self.dest))

    def progress(self):
        legs = self.legs()
        if legs is None:
            return None
        total = legs[0] + legs[1]
        return 0.0 if total <= 0 else min(max(legs[0] / total, 0.0), 1.0)


class RadarState:
    """Rotates through nearby aircraft, and remembers routes we've seen."""

    def __init__(self, home, radius_nm, hold_seconds=10, cache_size=16):
        self.home = home
        self.radius_nm = radius_nm
        self.hold = hold_seconds
        self.cache_size = cache_size
        self.aircraft = []
        self.current = None
        self.since = 0.0
        self.shown = []
        self.routes = {}

    def update_list(self, aircraft):
        self.aircraft = [a for a in aircraft
                         if _looks_airline(_callsign_of(a)) and a.get("lat") is not None]

    def due(self):
        """True when it's time to move to the next aircraft."""
        return self.current is None or time.monotonic() - self.since >= self.hold

    def choose(self):
        """Advance to the next aircraft, nearest-first, skipping recent ones.
        Returns the new current, or None if nothing is in range."""
        now = time.monotonic()
        cands = self.aircraft
        if not cands:
            self.current = None
            return None

        if self.current is not None and now - self.since < self.hold:
            for a in cands:
                if _callsign_of(a) == self.current.callsign:
                    self.current.apply_aircraft(a)
                    return self.current

        cands = sorted(cands,
                       key=lambda a: distance_nm(self.home, (a["lat"], a["lon"])))
        pick = None
        for a in cands:
            if _callsign_of(a) not in self.shown:
                pick = a
                break
        if pick is None:
            self.shown = []
            pick = cands[0]

        state = FlightState(_callsign_of(pick))
        state.apply_aircraft(pick)
        self.restore_route(state)
        self.current = state
        self.since = now
        self.shown.append(state.callsign)
        if len(self.shown) > self.cache_size:
            self.shown.pop(0)
        return state

    def skip(self):
        """Drop the current pick so the next choose() moves on."""
        self.current = None
        self.since = 0.0

    def remember_route(self, state):
        self.routes[state.callsign] = (
            state.route, state.orig, state.dest,
            state.orig_name, state.dest_name, state.logo, state.route_missing,
        )
        if len(self.routes) > self.cache_size:
            oldest = next(iter(self.routes))
            del self.routes[oldest]

    def restore_route(self, state):
        cached = self.routes.get(state.callsign)
        if cached is None:
            return False
        (state.route, state.orig, state.dest,
         state.orig_name, state.dest_name, state.logo, state.route_missing) = cached
        return True

    def range_of(self, state):
        """(distance_nm, compass_point) from home to the aircraft."""
        here = state.position
        if here is None:
            return None
        return (distance_nm(self.home, here),
                compass(bearing_deg(self.home, here)))
