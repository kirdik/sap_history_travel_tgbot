from typing import Any, Dict

import gpxpy


def parse_gpx(file_path: str) -> Dict[str, Any]:
    with open(file_path) as f:
        gpx = gpxpy.parse(f)

    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(
                    {
                        "lat": point.latitude,
                        "lon": point.longitude,
                        "elevation": point.elevation,
                        "time": point.time,
                    }
                )

    if not points:
        raise ValueError("No GPS points found in GPX file")

    return {"points": points, "name": gpx.tracks[0].name if gpx.tracks else "Unknown"}
