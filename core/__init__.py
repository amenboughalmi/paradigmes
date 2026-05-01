"""
Core module for Reactive vs Traditional IoT paradigm comparison.
"""

from .sensors import motion_sensor, temperature_sensor
from .engines import ReactiveEngine, TraditionalEngine
from .config import HIGH_TEMP_THRESHOLD, MAX_POINTS, WINDOW_SECONDS

__all__ = [
    "motion_sensor",
    "temperature_sensor",
    "ReactiveEngine",
    "TraditionalEngine",
    "HIGH_TEMP_THRESHOLD",
    "MAX_POINTS",
    "WINDOW_SECONDS",
]
