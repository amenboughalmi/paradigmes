import time
import threading
from collections import deque
from reactivex import operators as ops
from reactivex.subject import Subject

from .config import HIGH_TEMP_THRESHOLD, MAX_POINTS, WINDOW_SECONDS


class ReactiveEngine:
    def __init__(self, threshold, alerts_deque):
        self.threshold = threshold
        self.alerts = alerts_deque
        self.subject = Subject()

        self.temp_points = deque(maxlen=MAX_POINTS)
        self.motion_points = deque(maxlen=MAX_POINTS)
        self.high_temp_points = deque(maxlen=MAX_POINTS)

        self.total_alerts = 0
        self.motion_alerts = 0
        self.high_temp_alerts = 0
        self.latest_temp = 0.0

        self.event_latencies = deque(maxlen=100)
        self.last_alert_timestamp = 0

        self._subscriptions = []
        self._wire_pipeline()

    def _wire_pipeline(self):
        self._subscriptions.append(
            self.subject.pipe(
                ops.filter(lambda e: e["sensor"] == "temperature")
            ).subscribe(self._on_temperature)
        )

        self._subscriptions.append(
            self.subject.pipe(
                ops.filter(lambda e: e["sensor"] == "motion" and e["value"] == 1)
            ).subscribe(self._on_motion)
        )

        self._subscriptions.append(
            self.subject.pipe(
                ops.filter(lambda e: e["sensor"] == "temperature" and e["value"] > self.threshold)
            ).subscribe(self._on_high_temp)
        )

    def _on_temperature(self, event):
        ts = event["timestamp"]
        temp = float(event["value"])
        self.latest_temp = temp
        self.temp_points.append({"ts": ts, "temp": temp})

    def _on_motion(self, event):
        ts = event["timestamp"]
        latency = time.time() - ts
        self.event_latencies.append(latency)
        
        self.motion_alerts += 1
        self.total_alerts += 1
        self.motion_points.append({"ts": ts, "motion": 1})
        self.last_alert_timestamp = time.time()
        self.alerts.appendleft(f"[{time.strftime('%H:%M:%S')}] ⚡ REACTIVE MOTION (latency: {latency*1000:.1f}ms)")

    def _on_high_temp(self, event):
        ts = event["timestamp"]
        temp = float(event["value"])
        latency = time.time() - ts
        self.event_latencies.append(latency)
        
        self.high_temp_alerts += 1
        self.total_alerts += 1
        self.high_temp_points.append({"ts": ts, "high_temp": temp})
        self.last_alert_timestamp = time.time()
        self.alerts.appendleft(f"[{time.strftime('%H:%M:%S')}] ⚡ REACTIVE HIGH_TEMP {temp:.2f}°C (latency: {latency*1000:.1f}ms)")

    def get_avg_latency(self):
        if not self.event_latencies:
            return 0.0
        return sum(self.event_latencies) / len(self.event_latencies) * 1000

    def on_event(self, event):
        self.subject.on_next(event)

    def dispose(self):
        for subscription in self._subscriptions:
            subscription.dispose()


class TraditionalEngine:
    def __init__(self, threshold, alerts_deque, motion_sensor_gen, temp_sensor_gen):
        self.threshold = threshold
        self.alerts = alerts_deque
        self.running = True

        self.window_temp_values = []
        self.window_motion = 0
        self.window_high_temp = 0
        self.last_window_close = time.time()

        self.summary_points = deque(maxlen=MAX_POINTS)

        self.latest_avg_temp = 0.0
        self.total_alerts = 0
        self.motion_alerts = 0
        self.high_temp_alerts = 0

        self.window_latencies = deque(maxlen=100)
        
        self._event_queue = []
        self._queue_lock = threading.Lock()

        self._motion_thread = threading.Thread(
            target=self._run_motion_sensor,
            args=(motion_sensor_gen,),
            daemon=True
        )
        self._temp_thread = threading.Thread(
            target=self._run_temp_sensor,
            args=(temp_sensor_gen,),
            daemon=True
        )
        
        self._motion_thread.start()
        self._temp_thread.start()

    def _run_motion_sensor(self, generator):
        for event in generator():
            if not self.running:
                break
            with self._queue_lock:
                self._process_event(event)

    def _run_temp_sensor(self, generator):
        for event in generator():
            if not self.running:
                break
            with self._queue_lock:
                self._process_event(event)

    def _process_event(self, event):
        if event["sensor"] == "temperature":
            self.window_temp_values.append(float(event["value"]))
            if event["value"] > self.threshold:
                self.window_high_temp += 1
        elif event["sensor"] == "motion" and event["value"] == 1:
            self.window_motion += 1

    def tick(self, now_ts):
        if now_ts - self.last_window_close < WINDOW_SECONDS:
            return

        avg_temp = (
            sum(self.window_temp_values) / len(self.window_temp_values)
            if self.window_temp_values
            else self.latest_avg_temp
        )
        self.latest_avg_temp = avg_temp

        self.motion_alerts += self.window_motion
        self.high_temp_alerts += self.window_high_temp
        self.total_alerts += self.window_motion + self.window_high_temp

        window_latency = now_ts - self.last_window_close
        self.window_latencies.append(window_latency)

        self.summary_points.append(
            {
                "ts": now_ts,
                "avg_temp": round(avg_temp, 2),
                "motion_events": self.window_motion,
                "high_temp_events": self.window_high_temp,
            }
        )

        if self.window_motion > 0:
            self.alerts.appendleft(
                f"[{time.strftime('%H:%M:%S')}] 🕐 TRADITIONAL WINDOW MOTION {self.window_motion} (delay: {window_latency:.1f}s)"
            )
        if self.window_high_temp > 0:
            self.alerts.appendleft(
                f"[{time.strftime('%H:%M:%S')}] 🕐 TRADITIONAL WINDOW HIGH_TEMP {self.window_high_temp} (delay: {window_latency:.1f}s)"
            )

        self.window_temp_values.clear()
        self.window_motion = 0
        self.window_high_temp = 0
        self.last_window_close = now_ts

    def get_avg_latency(self):
        if not self.window_latencies:
            return WINDOW_SECONDS
        return sum(self.window_latencies) / len(self.window_latencies)

    def stop(self):
        self.running = False

