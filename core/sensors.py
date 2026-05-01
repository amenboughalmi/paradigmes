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
    while True:
        motion = random.choice([0, 1])
        yield {
            "sensor": "motion",
            "value": motion,
            "timestamp": time.time(),
        }
        time.sleep(random.uniform(*MOTION_SENSOR_INTERVAL))


def temperature_sensor():
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

