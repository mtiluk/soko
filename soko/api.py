import time

POSITION_API = "https://api.adsb.lol/v2/callsign/"
NEARBY_API = "https://api.adsb.lol/v2/point/{:.4f}/{:.4f}/{}"
ROUTE_API = "https://api.adsbdb.com/v0/callsign/"


class FlightAPI:
    def __init__(self, net):
        self.net = net

    def fetch_position(self, state):
        """Latest fix for state.callsign. Returns True if anything came back."""
        data, _ = self.net.get_json(POSITION_API + state.callsign)
        aircraft = (data or {}).get("ac") or []
        if not aircraft:
            return False
        state.apply_aircraft(aircraft[0])
        return True

    def fetch_nearby(self, lat, lon, radius_nm):
        """Raw aircraft records within radius_nm of (lat, lon)."""
        data, _ = self.net.get_json(NEARBY_API.format(lat, lon, int(radius_nm)))
        return (data or {}).get("ac") or []

    def fetch_route(self, state):
        """One-shot per flight: cached on success, dropped on a definite 404."""
        if state.route or state.route_missing:
            return False
        data, code = self.net.get_json(ROUTE_API + state.callsign)
        print("route:", state.callsign, code, bool(data))
        if code == 404:
            state.route_missing = True
            return False
        route = ((data or {}).get("response") or {}).get("flightroute")
        if not route:
            return False

        state.logo = (route.get("airline") or {}).get("icao") or ""

        origin = route.get("origin") or {}
        destination = route.get("destination") or {}
        state.orig_name = origin.get("municipality") or origin.get("name") or ""
        state.dest_name = destination.get("municipality") or destination.get("name") or ""

        if origin.get("latitude") is None or destination.get("latitude") is None:
            return False
        state.orig = (origin["latitude"], origin["longitude"])
        state.dest = (destination["latitude"], destination["longitude"])
        state.route = "{}-{}".format(
            origin.get("iata_code") or "?", destination.get("iata_code") or "?")
        return True
