import math
from datetime import datetime
from typing import Any, Dict, List


def calculate_metrics(points: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(points) < 2:
        raise ValueError("Need at least 2 points for calculation")

    total_distance = 0.0
    total_time = 0.0
    speeds = []
    elevations = []
    elevation_gain = 0.0

    prev_point = points[0]
    initial_elev = prev_point.get("elevation")
    if initial_elev is not None:
        elevations.append(initial_elev)

    for i in range(1, len(points)):
        point = points[i]

        distance = haversine_distance(
            prev_point["lat"], prev_point["lon"], point["lat"], point["lon"]
        )
        total_distance += distance

        if prev_point.get("time") and point.get("time"):
            time_diff = (point["time"] - prev_point["time"]).total_seconds()
            if time_diff > 0:
                speed = (distance / 1000) / (time_diff / 3600)
                speeds.append(speed)
                total_time += time_diff

        elev = point.get("elevation")
        if elev is not None:
            elevations.append(elev)

        prev_elev = prev_point.get("elevation")
        if elev is not None and prev_elev is not None:
            if elev > prev_elev:
                elevation_gain += elev - prev_elev

        prev_point = point

    min_elevation = min(elevations) if elevations else None
    max_elevation = max(elevations) if elevations else None

    avg_speed = sum(speeds) / len(speeds) if speeds else None
    max_speed = max(speeds) if speeds else None

    trip_time = points[0].get("time")
    trip_date = trip_time.date() if trip_time else datetime.now().date()

    return {
        "distance": total_distance,
        "duration": int(total_time),
        "avg_speed": avg_speed,
        "max_speed": max_speed,
        "min_elevation": min_elevation,
        "max_elevation": max_elevation,
        "elevation_gain": elevation_gain,
        "trip_date": trip_date,
    }


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance
