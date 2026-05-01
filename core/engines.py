"""
Processing engines: Traditional (windowed) vs Reactive (event-driven).
Both engines track performance metrics to highlight reactive paradigm advantages.
"""

import time
from collections import deque
from reactivex import operators as ops
from reactivex.subject import Subject

from .config import HIGH_TEMP_THRESHOLD, MAX_POINTS, WINDOW_SECONDS


class ReactiveEngine:
    """
    Event-driven reactive engine using RxPY Subject.
    Responds IMMEDIATELY to events with low latency.
    
    Tracks:
    - Individual sensor readings (temperature, motion)
    - High-temperature events
    - Performance metrics (latency, responsiveness)
    """
    
    def __init__(self, threshold, alerts_deque):
        self.threshold = threshold
        self.alerts = alerts_deque
        self.subject = Subject()

        # Data buffers
        self.temp_points = deque(maxlen=MAX_POINTS)
        self.motion_points = deque(maxlen=MAX_POINTS)
        self.high_temp_points = deque(maxlen=MAX_POINTS)

        # Counters
        self.total_alerts = 0
        self.motion_alerts = 0
        self.high_temp_alerts = 0
        self.latest_temp = 0.0

        # Performance metrics
        self.event_latencies = deque(maxlen=100)  # Track how fast we respond
        self.last_alert_timestamp = 0

        self._subscriptions = []
        self._wire_pipeline()

    def _wire_pipeline(self):
        """Set up reactive subscriptions with immediate processing."""
        
        # Temperature stream: track all readings
        self._subscriptions.append(
            self.subject.pipe(
                ops.filter(lambda e: e["sensor"] == "temperature")
            ).subscribe(self._on_temperature)
        )

        # Motion stream: immediate detection
        self._subscriptions.append(
            self.subject.pipe(
                ops.filter(lambda e: e["sensor"] == "motion" and e["value"] == 1)
            ).subscribe(self._on_motion)
        )

        # High-temperature stream: immediate alert
        self._subscriptions.append(
            self.subject.pipe(
                ops.filter(lambda e: e["sensor"] == "temperature" and e["value"] > self.threshold)
            ).subscribe(self._on_high_temp)
        )

    def _on_temperature(self, event):
        """React immediately to temperature reading."""
        ts = event["timestamp"]
        temp = float(event["value"])
        self.latest_temp = temp
        self.temp_points.append({"ts": ts, "temp": temp})

    def _on_motion(self, event):
        """React immediately to motion detection."""
        ts = event["timestamp"]
        latency = time.time() - ts
        self.event_latencies.append(latency)
        
        self.motion_alerts += 1
        self.total_alerts += 1
        self.motion_points.append({"ts": ts, "motion": 1})
        self.last_alert_timestamp = time.time()
        self.alerts.appendleft(f"[{time.strftime('%H:%M:%S')}] ⚡ REACTIVE MOTION (latency: {latency*1000:.1f}ms)")

    def _on_high_temp(self, event):
        """React immediately to high temperature."""
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
        """Average latency in milliseconds."""
        if not self.event_latencies:
            return 0.0
        return sum(self.event_latencies) / len(self.event_latencies) * 1000

    def on_event(self, event):
        """Feed event into the reactive pipeline."""
        self.subject.on_next(event)

    def dispose(self):
        """Clean up subscriptions."""
        for subscription in self._subscriptions:
            subscription.dispose()


class TraditionalEngine:
    """
    Windowed traditional engine with callbacks and manual state management.
    Aggregates events into 5-second windows and processes them in BATCHES.
    
    Shows the delayed, batch-processing nature of traditional approaches.
    Tracks same metrics to highlight the latency difference.
    """
    
    def __init__(self, threshold, alerts_deque):
        self.threshold = threshold
        self.alerts = alerts_deque

        # Window state
        self.window_temp_values = []
        self.window_motion = 0
        self.window_high_temp = 0
        self.last_window_close = time.time()

        # Data buffers
        self.summary_points = deque(maxlen=MAX_POINTS)

        # Counters
        self.latest_avg_temp = 0.0
        self.total_alerts = 0
        self.motion_alerts = 0
        self.high_temp_alerts = 0

        # Performance metrics
        self.window_latencies = deque(maxlen=100)  # How long until window closes

    def on_event(self, event):
        """Receive event and buffer it (no immediate reaction)."""
        if event["sensor"] == "temperature":
            self.window_temp_values.append(float(event["value"]))
            if event["value"] > self.threshold:
                self.window_high_temp += 1
        elif event["sensor"] == "motion" and event["value"] == 1:
            self.window_motion += 1

    def tick(self, now_ts):
        """
        Check if window should close and process accumulated events.
        This is called periodically - introducing DELAY between event and processing.
        """
        if now_ts - self.last_window_close < WINDOW_SECONDS:
            return

        # Calculate window metrics
        avg_temp = (
            sum(self.window_temp_values) / len(self.window_temp_values)
            if self.window_temp_values
            else self.latest_avg_temp
        )
        self.latest_avg_temp = avg_temp

        # Accumulate totals
        self.motion_alerts += self.window_motion
        self.high_temp_alerts += self.window_high_temp
        self.total_alerts += self.window_motion + self.window_high_temp

        # Record window metrics
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

        # Generate delayed alerts
        if self.window_motion > 0:
            self.alerts.appendleft(
                f"[{time.strftime('%H:%M:%S')}] 🕐 TRADITIONAL WINDOW MOTION {self.window_motion} (delay: {window_latency:.1f}s)"
            )
        if self.window_high_temp > 0:
            self.alerts.appendleft(
                f"[{time.strftime('%H:%M:%S')}] 🕐 TRADITIONAL WINDOW HIGH_TEMP {self.window_high_temp} (delay: {window_latency:.1f}s)"
            )

        # Reset window
        self.window_temp_values.clear()
        self.window_motion = 0
        self.window_high_temp = 0
        self.last_window_close = now_ts

    def get_avg_latency(self):
        """Average latency in seconds (window size)."""
        if not self.window_latencies:
            return WINDOW_SECONDS
        return sum(self.window_latencies) / len(self.window_latencies)
