import time
import reactivex as rx
from reactivex import operators as ops
from reactivex.scheduler import ThreadPoolScheduler

from sensors import motion_sensor, temperature_sensor

scheduler = ThreadPoolScheduler(4)


def create_sensor_observable(generator_func, name: str):
    def subscribe(observer, scheduler=None):
        try:
            for data in generator_func():
                observer.on_next(data)
        except Exception as e:
            observer.on_error(e)

    return rx.create(subscribe).pipe(
        ops.subscribe_on(scheduler),
        ops.do_action(lambda d: print(f"   [RAW {name.upper()}] {d}"))  # For debugging
    )


def create_reactive_pipeline():
    motion_obs = create_sensor_observable(motion_sensor, "motion")
    temp_obs   = create_sensor_observable(temperature_sensor, "temp")

    # === Rich Reactive Logic ===
    # 1. Debounce motion: only consider motion if no new motion for 1.5 seconds (avoids noise)
    debounced_motion = motion_obs.pipe(
        ops.filter(lambda d: d["value"] == 1),   # only motion detected
        ops.debounce(1.5)                        # ← Key operator for IoT
    )

    # 2. Filter high temperature
    high_temp = temp_obs.pipe(
        ops.filter(lambda d: d["value"] > 25.0)
    )

    # 3. Merge filtered streams + combine latest temperature with motion
    merged = rx.merge(debounced_motion, high_temp)

    pipeline = merged.pipe(
        # Enrich with alert
        ops.map(lambda d: {
            **d,
            "alert_level": "HIGH_TEMP" if d["sensor"] == "temperature" else "MOTION_DETECTED"
        }),

        # Individual filtered events (great for demo)
        ops.do_action(lambda d: print(f"[REACTIVE EVENT] {time.strftime('%H:%M:%S')} - {d['alert_level']} | Value: {d['value']}")),

        # Aggregate every 5 seconds
        ops.buffer_with_time(5.0),

        ops.map(lambda buffer: {
            "window_end": time.strftime('%H:%M:%S'),
            "motion_detections": sum(1 for d in buffer if d["sensor"] == "motion"),
            "high_temp_readings": sum(1 for d in buffer if d["sensor"] == "temperature"),
            "avg_temp": round(
                sum(d["value"] for d in buffer if d["sensor"] == "temperature") /
                max(1, sum(1 for d in buffer if d["sensor"] == "temperature")), 2
            ) if any(d["sensor"] == "temperature" for d in buffer) else 0.0,
            "total_alerts": len(buffer)
        })
    )
        # Return both: the processed pipeline (for console) and raw merged for visualization
    return pipeline, merged   # merged contains ALL sensor data
    