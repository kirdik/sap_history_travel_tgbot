import math
import os
from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams["font.family"] = "DejaVu Sans"


def create_infographic(metrics: dict, output_path: str):
    has_elevation = metrics.get("min_elevation") is not None

    # Adjust figure layout based on whether elevation data exists
    if has_elevation:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    else:
        fig, ax1 = plt.subplots(1, 1, figsize=(10, 5))

    # --- Plot Speed ---
    speed_data = generate_speed_data(metrics)
    ax1.plot(speed_data["times"], speed_data["speeds"], color="#3498db", linewidth=2)
    ax1.set_title("Скорость", fontsize=12, fontweight="bold")
    ax1.set_ylabel("км/ч")
    ax1.grid(True, alpha=0.3)
    ax1.fill_between(
        speed_data["times"], speed_data["speeds"], alpha=0.3, color="#3498db"
    )

    # --- Plot Elevation (if available) ---
    if has_elevation:
        elevation_data = generate_elevation_data(metrics)
        ax2.plot(
            elevation_data["distances"],
            elevation_data["elevations"],
            color="#27ae60",
            linewidth=2,
        )
        ax2.set_title("Высота", fontsize=12, fontweight="bold")
        ax2.set_xlabel("Расстояние (км)")
        ax2.set_ylabel("м")
        ax2.grid(True, alpha=0.3)
        ax2.fill_between(
            elevation_data["distances"],
            elevation_data["elevations"],
            alpha=0.3,
            color="#27ae60",
        )

    # --- Add Summary Text ---
    fig.text(
        0.5,
        0.95,
        get_summary_text(metrics),
        ha="center",
        va="top",
        fontsize=11,
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    plt.tight_layout()
    plt.subplots_adjust(top=0.85 if has_elevation else 0.8)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()


def generate_speed_data(metrics):
    duration_hours = (metrics.get("duration") or 0) / 3600
    points = max(10, int(duration_hours * 2))
    times = list(range(points))
    avg_speed = metrics.get("avg_speed") or 0
    max_speed = metrics.get("max_speed") or 0
    # Ensure max_speed is not less than avg_speed to avoid negative values
    if max_speed < avg_speed:
        max_speed = avg_speed
    speeds = [
        min(avg_speed + (max_speed - avg_speed) * abs(0.5 - i / points) * 2, max_speed)
        for i in range(points)
    ]
    return {"times": times, "speeds": speeds}


def generate_elevation_data(metrics):
    distance_km = (metrics.get("distance") or 0) / 1000
    points = max(20, int(distance_km * 10))
    distances = [i * distance_km / points for i in range(points)]

    min_elev = metrics.get("min_elevation") or 0
    max_elev = metrics.get("max_elevation") or 0
    # Ensure max_elev is not less than min_elev
    if max_elev < min_elev:
        max_elev = min_elev

    elevations = [
        min_elev
        + (max_elev - min_elev) * (0.5 + 0.5 * math.sin(i / points * 4 * math.pi))
        for i in range(points)
    ]
    return {"distances": distances, "elevations": elevations}


def get_summary_text(metrics):
    date_str = (metrics.get("trip_date") or datetime.now().date()).strftime("%d.%m.%Y")
    distance = (metrics.get("distance") or 0) / 1000
    duration = metrics.get("duration") or 0
    duration_str = f"{duration // 3600}ч {(duration % 3600) // 60}м"
    avg_speed = metrics.get("avg_speed") or 0
    max_speed = metrics.get("max_speed") or 0

    text_parts = [
        f"📊 {date_str} | {distance:.1f} км | {duration_str}",
        f"⚡ {avg_speed:.1f} км/ч (средняя), {max_speed:.1f} км/ч (макс)",
    ]

    min_elev = metrics.get("min_elevation")
    if min_elev is not None:
        max_elev = metrics.get("max_elevation") or 0
        gain = metrics.get("elevation_gain") or 0
        text_parts.append(f"⛰️ {min_elev:.0f}-{max_elev:.0f} м, набор: {gain:.0f} м")

    return "\n".join(text_parts)
