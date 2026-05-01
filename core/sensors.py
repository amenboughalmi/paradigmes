"""
Simulated IoT sensor generators.
Produces infinite streams of sensor readings with realistic behavior.
"""

import random
import time
from .config import (
    MOTION_SENSOR_INTERVAL,
    TEMPERATURE_SENSOR_INTERVAL,
    TEMPERATURE_FLUCTUATION,
    TEMPERATURE_MIN,
    TEMPERATURE_MAX,
    TEMPERATURE_INITIAL,
)


def motion_sensor():
    """
    Simulates a motion sensor: emits 0 (no motion) or 1 (motion detected).
    
    Yields:
        dict: {"sensor": "motion", "value": 0|1, "timestamp": float}
    """
    while True:
        motion = random.choice([0, 1])
        yield {
            "sensor": "motion",
            "value": motion,
            "timestamp": time.time(),
        }
        time.sleep(random.uniform(*MOTION_SENSOR_INTERVAL))


def temperature_sensor():
    """
    Simulates a temperature sensor: emits floating-point temperature readings.
    Temperature fluctuates realistically with small random drift.
    
    Yields:
        dict: {"sensor": "temperature", "value": float, "timestamp": float}
    """
    temp = TEMPERATURE_INITIAL
    while True:
        drift = random.uniform(*TEMPERATURE_FLUCTUATION)
        temp = min(TEMPERATURE_MAX, max(TEMPERATURE_MIN, temp + drift))
        
        yield {
            "sensor": "temperature",
            "value": round(temp, 2),
            "timestamp": time.time(),
        }
        time.sleep(random.uniform(*TEMPERATURE_SENSOR_INTERVAL))
