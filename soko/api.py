import time

POSITION_API = "https://api.adsb.lol/v2/callsign/"
ROUTE_API = "https://api.adsbdb.com/v0/callsign/"

def _number(value):
    return value if isinstance(value, (int, float)) else None

class FlightAPI:
    def __init__(self, net):
        self.net = net

    def fetch_position(self, state):
        data, _ = self.net.get_json(POSITION_API + state.callsign)
        aircraft = (data or {}).get("ac") or []
        if not aircraft:
            return False

        a = aircraft[0]
        state.actype = a.get("t") or state.actype
        state.lat = a.get("lat")
        state.lon = a.get("lon")
        state.gs = _number(a.get("gs"))
        state.alt = _number(a.get("alt_baro"))
        state.last_seen = time.monotonic()
        return True

    def fetch_route(self, state):
        if state.route or state.route_missing:
            return False

        data, code = self.net.get_json(ROUTE_API + state.callsign)
        if code == 404:
            state.route_missing = True
            return False

        route = ((data or {}).get("response") or {}).get("flightroute")
        if not route:
            return False

        origin = route.get("origin") or {}
        destination = route.get("destination") or {}
        if origin.get("latitude") is None or destination.get("latitude") is None:
            return False

        state.orig = (origin["latitude"], origin["longitude"])
        state.dest = (destination["latitude"], destination["longitude"])
        state.route = "{}-{}".format(
            origin.get("iata_code") or "?", destination.get("iata_code") or "?")
        return True
