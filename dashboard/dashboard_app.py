import random
import sys
import time
from pathlib import Path
from collections import deque
import altair as alt
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.engines import ReactiveEngine, TraditionalEngine
from core.sensors import motion_sensor, temperature_sensor
from core.config import HIGH_TEMP_THRESHOLD, WINDOW_SECONDS

MAX_POINTS = 160
ALERT_REFRESH_MS = 350
TEMP_MIN = 15.0
TEMP_MAX = 30.0


def init_state():
    defaults = {
        "running": False,
        "mode": "Both",
        "threshold": HIGH_TEMP_THRESHOLD,
        "speed": 1.0,
        "sim_temp": 20.0,
        "last_tick": time.time(),
        "next_motion_ts": time.time() + 0.35,
        "next_temp_ts": time.time() + 0.55,
        "alerts": deque(maxlen=15),
        "reactive_engine": None,
        "traditional_engine": None,
        "threshold_signature": None,
        "last_mode_signature": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_simulation_state():
    st.session_state.sim_temp = 20.0
    now_ts = time.time()
    st.session_state.last_tick = now_ts
    st.session_state.next_motion_ts = now_ts + 0.35
    st.session_state.next_temp_ts = now_ts + 0.55
    st.session_state.alerts.clear()

    if st.session_state.reactive_engine is not None:
        st.session_state.reactive_engine.dispose()
    if st.session_state.traditional_engine is not None:
        st.session_state.traditional_engine.stop()
    st.session_state.reactive_engine = None
    st.session_state.traditional_engine = None
    st.session_state.threshold_signature = None
    st.session_state.last_mode_signature = None


def start_simulation_now():
    now_ts = time.time()
    st.session_state.running = True
    st.session_state.last_tick = now_ts
    st.session_state.next_motion_ts = now_ts + 0.35
    st.session_state.next_temp_ts = now_ts + 0.55

    if st.session_state.traditional_engine is not None:
        st.session_state.traditional_engine.last_window_close = now_ts


def ensure_engines(mode, threshold):
    threshold_signature = f"{mode}:{threshold:.2f}"
    mode_signature = mode

    if st.session_state.threshold_signature != threshold_signature or st.session_state.last_mode_signature != mode_signature:
        if st.session_state.reactive_engine is not None:
            st.session_state.reactive_engine.dispose()
        if st.session_state.traditional_engine is not None:
            st.session_state.traditional_engine.stop()

        if mode in ("Reactive", "Both"):
            st.session_state.reactive_engine = ReactiveEngine(threshold, st.session_state.alerts)
        else:
            st.session_state.reactive_engine = None

        if mode in ("Traditional", "Both"):
            st.session_state.traditional_engine = TraditionalEngine(
                threshold, st.session_state.alerts, motion_sensor, temperature_sensor
            )
        else:
            st.session_state.traditional_engine = None

        st.session_state.threshold_signature = threshold_signature
        st.session_state.last_mode_signature = mode_signature


def generate_events(until_ts):
    events = []
    speed = max(0.4, st.session_state.speed)

    while st.session_state.next_motion_ts <= until_ts:
        events.append(
            {
                "sensor": "motion",
                "value": random.choice([0, 1]),
                "timestamp": st.session_state.next_motion_ts,
            }
        )
        st.session_state.next_motion_ts += random.uniform(0.45, 1.25) / speed

    while st.session_state.next_temp_ts <= until_ts:
        baseline = 20.0
        reversion = (baseline - st.session_state.sim_temp) * 0.12
        noise = random.uniform(-0.25, 0.25)
        spike = random.uniform(1.8, 3.2) if random.random() < 0.03 else 0.0
        next_temp = st.session_state.sim_temp + reversion + noise + spike
        st.session_state.sim_temp = min(24.8, max(17.5, next_temp))
        events.append(
            {
                "sensor": "temperature",
                "value": round(st.session_state.sim_temp, 2),
                "timestamp": st.session_state.next_temp_ts,
            }
        )
        st.session_state.next_temp_ts += random.uniform(0.75, 1.45) / speed

    events.sort(key=lambda item: item["timestamp"])
    return events


def update_simulation(mode):
    now_ts = time.time()
    events = generate_events(now_ts)

    reactive_engine = st.session_state.reactive_engine
    traditional_engine = st.session_state.traditional_engine

    for event in events:
        if reactive_engine is not None:
            reactive_engine.on_event(event)

    if traditional_engine is not None:
        traditional_engine.tick(now_ts)

    st.session_state.last_tick = now_ts


def render_header():
    st.markdown(
        """
        <style>
            .main {background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%);} 
            div[data-testid="stMetric"] {
                background: linear-gradient(135deg, rgba(33,46,81,0.9), rgba(18,27,49,0.95));
                border: 2px solid rgba(125,153,214,0.5);
                border-radius: 14px;
                padding: 0.8rem 1rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            }
            .block-container {padding-top: 1.0rem; padding-bottom: 1.2rem;}
            .section-title {
                font-size: 1.15rem; 
                font-weight: 700; 
                letter-spacing: 0.6px;
                text-transform: uppercase;
                background: linear-gradient(90deg, #64b5f6, #90caf9);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .paradigm-badge {
                display: inline-block;
                padding: 0.4rem 0.8rem;
                border-radius: 8px;
                font-weight: 600;
                font-size: 0.9rem;
            }
            .reactive-badge {
                background: linear-gradient(135deg, #4caf50, #45a049);
                color: white;
            }
            .traditional-badge {
                background: linear-gradient(135deg, #ff9800, #f57c00);
                color: white;
            }
            .latency-indicator {
                font-family: 'Courier New', monospace;
                font-weight: bold;
                padding: 0.3rem 0.6rem;
                border-radius: 4px;
                display: inline-block;
            }
            .latency-fast { background: #c8e6c9; color: #1b5e20; }
            .latency-slow { background: #ffe0b2; color: #e65100; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("⚡ Reactive vs Traditional IoT Dashboard")


def render_controls():
    col1, col2, col3, col4, col5 = st.columns([1.1, 1.2, 1.2, 1.0, 0.9])

    with col1:
        mode = st.radio(
            "**Paradigm**",
            options=["Traditional", "Reactive", "Both"],
            index=["Traditional", "Reactive", "Both"].index(st.session_state.mode),
            horizontal=True,
        )

    with col2:
        threshold = st.slider(
            "**Temperature Threshold (°C)**",
            19.0, 24.0,
            float(st.session_state.threshold),
            0.1,
            label_visibility="collapsed"
        )

    with col3:
        speed = st.slider(
            "**Event Rate (Simulation Speed)**",
            0.5, 3.0,
            float(st.session_state.speed),
            0.1,
            label_visibility="collapsed"
        )

    with col4:
        start, stop, reset = st.columns(3, gap="small")
        with start:
            if st.button("▶ Start", use_container_width=True):
                start_simulation_now()
        with stop:
            if st.button("⏸ Stop", use_container_width=True):
                st.session_state.running = False
        with reset:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.running = False
                reset_simulation_state()

    with col5:
        status_text = "🟢 LIVE" if st.session_state.running else "⚪ IDLE"
        st.metric("Status", status_text)

    st.session_state.mode = mode
    st.session_state.threshold = threshold
    st.session_state.speed = speed
    ensure_engines(mode, threshold)


def _to_chart_df(points, x_col="ts"):
    if not points:
        return pd.DataFrame(columns=["time"])

    df = pd.DataFrame(list(points))
    df["time"] = pd.to_datetime(df[x_col], unit="s")
    return df


def _render_temp_chart(df, value_col, color="#4caf50"):
    if df.empty:
        return
    chart = (
        alt.Chart(df)
        .mark_line(color=color, size=2)
        .encode(
            x=alt.X("time:T"),
            y=alt.Y(f"{value_col}:Q", scale=alt.Scale(domain=[TEMP_MIN, TEMP_MAX])),
        )
        .properties(height=250)
    )
    st.altair_chart(chart, width="stretch")


def render_traditional_panel(panel):
    engine = st.session_state.traditional_engine
    
    with panel:
        st.markdown(
            "<div class='section-title'>🕐 Traditional Pipeline (Windowed, Batch Processing)</div>",
            unsafe_allow_html=True
        )

        if engine is None:
            st.info("Traditional mode is not active.")
            return

        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.metric(
                "Avg Temp",
                f"{engine.latest_avg_temp:.1f}°C",
                delta=f"Threshold: {st.session_state.threshold:.1f}°C"
            )
        
        with m2:
            st.metric("Motion Events", str(engine.motion_alerts))
        
        with m3:
            st.metric("High-Temp Events", str(engine.high_temp_alerts))
        
        with m4:
            avg_latency = engine.get_avg_latency()
            st.markdown(
                f"<div class='latency-indicator latency-slow'>Latency: {avg_latency:.1f}s</div>",
                unsafe_allow_html=True
            )
            st.caption("Average window delay")

        st.subheader("Temperature Trend", divider="orange")
        summary_df = _to_chart_df(engine.summary_points)
        
        if not summary_df.empty:
            _render_temp_chart(summary_df, "avg_temp", "#ff9800")
        else:
            st.info("Waiting for first 5-second window to close...")

        st.subheader("Per-Window Event Counts", divider="orange")
        col_motion, col_temp = st.columns(2)
        
        with col_motion:
            st.markdown("**Motion Detections per Window**")
            if not summary_df.empty:
                motion_counts_df = summary_df.set_index("time")[["motion_events"]].rename(
                    columns={"motion_events": "Motion detections per window"}
                )
                st.bar_chart(motion_counts_df, height=200)
            else:
                st.info("No data yet")
        
        with col_temp:
            st.markdown("**High-Temperature Readings per Window**")
            if not summary_df.empty:
                high_temp_counts_df = summary_df.set_index("time")[["high_temp_events"]].rename(
                    columns={"high_temp_events": "High-temp readings per window"}
                )
                st.bar_chart(high_temp_counts_df, height=200)
            else:
                st.info("No data yet")


def render_reactive_panel(panel):
    engine = st.session_state.reactive_engine
    
    with panel:
        st.markdown(
            "<div class='section-title'>⚡ Reactive Pipeline (Event-Driven, Immediate)</div>",
            unsafe_allow_html=True
        )

        if engine is None:
            st.info("Reactive mode is not active.")
            return

        m1, m2, m3, m4 = st.columns(4)
        
        with m1:
            st.metric(
                "Current Temp",
                f"{engine.latest_temp:.1f}°C",
                delta=f"Threshold: {st.session_state.threshold:.1f}°C"
            )
        
        with m2:
            st.metric("Motion Detections", str(engine.motion_alerts))
        
        with m3:
            st.metric("High-Temp Alerts", str(engine.high_temp_alerts))
        
        with m4:
            avg_latency = engine.get_avg_latency()
            latency_class = "latency-fast" if avg_latency < 300 else "latency-slow"
            st.markdown(
                f"<div class='latency-indicator {latency_class}'>Latency: {avg_latency:.1f}ms</div>",
                unsafe_allow_html=True
            )
            st.caption("Average response time")

        st.subheader("Real-Time Temperature", divider="green")
        temp_df = _to_chart_df(engine.temp_points)
        
        if not temp_df.empty:
            _render_temp_chart(temp_df, "temp", "#4caf50")
        else:
            st.info("Waiting for first temperature reading...")

        st.subheader("High-Temperature Events", divider="green")
        col_high_temp, col_motion = st.columns(2)
        
        with col_high_temp:
            st.markdown("**High-Temperature Detections**")
            high_df = _to_chart_df(engine.high_temp_points)
            if not high_df.empty:
                st.area_chart(high_df.set_index("time")[["high_temp"]], height=200, color="#ff5252")
            else:
                st.info("No high-temp events yet")
        
        with col_motion:
            st.markdown("**Motion Detections**")
            motion_df = _to_chart_df(engine.motion_points)
            if not motion_df.empty:
                st.bar_chart(motion_df.set_index("time")[["motion"]], height=200, color="#76ff03")
            else:
                st.info("No motion detected yet")



def render_comparison_insights():
    st.divider()
    
    col_insight1, col_insight2 = st.columns(2)
    
    with col_insight1:
        st.markdown("""
        #### 🕐 Traditional (Windowed)
        - **5-second batch windows** aggregate events
        - **Delayed processing** until window closes
        - **Lower CPU per event** (batched)
        - **Useful for**: Reports, analytics, backpressure
        - **Latency**: ~5 seconds
        """)
    
    with col_insight2:
        st.markdown("""
        #### ⚡ Reactive (Event-Driven)
        - **Immediate response** to events
        - **Individual event processing** with low latency
        - **Higher responsiveness** for alerts/actions
        - **Useful for**: Real-time control, IoT, alerts
        - **Latency**: <300ms
        """)


def main():
    st.set_page_config(
        page_title="Reactive IoT Dashboard",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    init_state()
    render_header()
    render_controls()

    if st.session_state.running:
        update_simulation(st.session_state.mode)

    if st.session_state.mode == "Both":
        left, right = st.columns(2)
        render_traditional_panel(left)
        render_reactive_panel(right)
    elif st.session_state.mode == "Traditional":
        render_traditional_panel(st.container())
    else:
        render_reactive_panel(st.container())

    render_comparison_insights()

    if st.session_state.running:
        time.sleep(ALERT_REFRESH_MS / 1000)
        st.rerun()


if __name__ == "__main__":
    main()
