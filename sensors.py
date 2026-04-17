import random
import time
from threading import Thread
import reactivex as rx
from reactivex import operators as ops
from reactivex.scheduler import ThreadPoolScheduler

# Shared scheduler for concurrency
scheduler = ThreadPoolScheduler(2)  # 2 threads for 2 sensors

def motion_sensor():
    """Simulates motion sensor: emits 0 or 1 randomly every 0.5-1.5s"""
    while True:
        motion = random.choice([0, 1])  # 0 = no motion, 1 = motion detected
        yield {"sensor": "motion", "value": motion, "timestamp": time.time()}
        time.sleep(random.uniform(0.5, 1.5))

def temperature_sensor():
    """Simulates temperature sensor: emits value every 1-2s"""
    temp = 20.0
    while True:
        temp += random.uniform(-0.5, 0.5)  # small fluctuation
        yield {"sensor": "temperature", "value": round(temp, 2), "timestamp": time.time()}
        time.sleep(random.uniform(1.0, 2.0))