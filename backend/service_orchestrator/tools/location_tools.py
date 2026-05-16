"""
Location tools for the Service Orchestrator.
Uses the Haversine formula to calculate distances between Islamabad sectors.
No external API needed.
"""

import json
import math
import os

# Load sector coordinates
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
with open(os.path.join(_DATA_DIR, "locations.json"), "r") as f:
    _LOCATIONS = json.load(f)["sectors"]


def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate distance between two lat/lng points in kilometers."""
    R = 6371  # Earth radius in km
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def calculate_distance(sector_from: str, sector_to: str) -> dict:
    """Calculate the distance in km between two Islamabad sectors.

    Args:
        sector_from: The origin sector name (e.g. 'G-13', 'F-10', 'I-8').
        sector_to: The destination sector name.

    Returns:
        A dict with distance_km, estimated_travel_time_min, and status.
    """
    s_from = sector_from.upper().strip()
    s_to = sector_to.upper().strip()

    if s_from not in _LOCATIONS:
        return {"status": "error", "message": f"Unknown sector: {sector_from}. Known sectors: {', '.join(sorted(_LOCATIONS.keys()))}"}
    if s_to not in _LOCATIONS:
        return {"status": "error", "message": f"Unknown sector: {sector_to}. Known sectors: {', '.join(sorted(_LOCATIONS.keys()))}"}

    loc_from = _LOCATIONS[s_from]
    loc_to = _LOCATIONS[s_to]

    distance = _haversine(loc_from["lat"], loc_from["lng"], loc_to["lat"], loc_to["lng"])
    # Estimate travel time: avg 25 km/h in Islamabad urban traffic
    travel_time = round((distance / 25) * 60, 0)

    return {
        "status": "success",
        "sector_from": s_from,
        "sector_to": s_to,
        "distance_km": distance,
        "estimated_travel_time_min": int(max(travel_time, 5)),
        "area_from": loc_from["area"],
        "area_to": loc_to["area"],
    }


def get_sector_coordinates(sector_name: str) -> dict:
    """Get the latitude and longitude coordinates for a given Islamabad sector.

    Args:
        sector_name: The sector name (e.g. 'G-13', 'F-10').

    Returns:
        A dict with lat, lng, area name, and status.
    """
    s = sector_name.upper().strip()
    if s not in _LOCATIONS:
        return {"status": "error", "message": f"Unknown sector: {sector_name}. Known sectors: {', '.join(sorted(_LOCATIONS.keys()))}"}

    loc = _LOCATIONS[s]
    return {
        "status": "success",
        "sector": s,
        "lat": loc["lat"],
        "lng": loc["lng"],
        "area": loc["area"],
    }


def get_all_sectors() -> dict:
    """Get a list of all known Islamabad sectors with their coordinates.

    Returns:
        A dict with all sector names and their coordinates.
    """
    return {
        "status": "success",
        "total_sectors": len(_LOCATIONS),
        "sectors": {k: {"lat": v["lat"], "lng": v["lng"], "area": v["area"]} for k, v in _LOCATIONS.items()},
    }
