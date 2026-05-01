# Programming Language Paradigms: Reactive vs Traditional

A **comprehensive project demonstrating reactive programming paradigm in Python** through a side-by-side comparison with traditional callback-based approaches. Built for a programming language course, this project showcases the advantages of reactive programming in IoT sensor systems.

## 🎯 Project Goals

- **Compare paradigms** side-by-side in a real-time, interactive dashboard
- **Highlight advantages** of reactive programming (low latency, immediate responsiveness)
- **Demonstrate RxPY** as a practical reactive framework for Python
- **Create presentation-ready visuals** with clear paradigm differences

## 🏗️ Project Structure

```
paradigmes#/
├── core/
│   ├── __init__.py
│   ├── config.py              # Shared configuration
│   ├── sensors.py             # IoT sensor simulators
│   └── engines.py             # Processing engines (Reactive & Traditional)
├── dashboard/
│   ├── dashboard_app.py       # Streamlit dashboard (MAIN ENTRY POINT)
│   ├── config.py              # Dashboard configuration
│   └── README.md              # Dashboard documentation
├── README.md                  # This file
└── [legacy files]             # main.py, visualization.py, etc. (for reference)
```

## 🚀 Getting Started

### Installation

```bash
# Install dependencies
pip install streamlit pandas reactivex

# Navigate to project directory
cd paradigmes#

# Run the dashboard
streamlit run dashboard/dashboard_app.py
```

### Quick Demo

1. Open the dashboard (default: `http://localhost:8501`)
2. Select **"Both"** mode for side-by-side comparison
3. Set **Temperature Threshold** to ~21°C
4. Click **Start** button
5. **Watch the paradigm differences unfold**:
   - ⚡ **Reactive**: Alerts appear instantly (<50ms)
   - 🕐 **Traditional**: Alerts appear after 5-second window closes

## 📊 Key Features

### ⚡ Reactive Pipeline (Event-Driven)
- **RxPY Observable streams** with rich operators
- **Immediate event processing** with <100ms latency
- **Individual event responses** for alerts
- **Real-time charts** updated per event
- Demonstrates: debounce, filter, map, buffer_with_time operators

### 🕐 Traditional Pipeline (Windowed)
- **Callback-based** event handling
- **5-second aggregation windows** for batch processing
- **Threading + queues** for concurrency management
- **Delayed responses** (~2.5-5 seconds typical)
- Demonstrates: manual state management, thread coordination

### 📈 Interactive Dashboard
- **Live metrics** showing current vs windowed data
- **Latency indicators** comparing response times (ms vs seconds)
- **Color-coded alerts** distinguishing paradigm sources
- **Simulation controls** for speed and threshold tuning
- **Side-by-side mode** for direct comparison

## 💡 What Gets Visualized

### For Screenshots & Presentations:

1. **Metrics Panels**
   - Current temperature (Reactive) vs windowed average (Traditional)
   - Alert counts
   - **Latency comparison** (the key differentiator!)

2. **Charts**
   - Temperature trends over time
   - Motion detection spikes
   - High-temperature events
   - Reactive: per-event data | Traditional: aggregated data

3. **Alert Feed**
   - ⚡ Reactive alerts (instant, with millisecond latencies)
   - 🕐 Traditional alerts (batched, with multi-second delays)
   - Color-coded for easy identification

## 🔧 Core Components

### Sensor Simulation (`core/sensors.py`)
- **Motion Sensor**: Random 0/1 events every 0.5-1.5 seconds
- **Temperature Sensor**: Realistic fluctuation with drift

### Reactive Engine (`core/engines.py`)
```python
ReactiveEngine(threshold, alerts_deque)
# - RxPY Subject-based event processing
# - Immediate subscriptions to temperature, motion, high-temp streams
# - Latency tracking in milliseconds
# - Individual event responses
```

### Traditional Engine (`core/engines.py`)
```python
TraditionalEngine(threshold, alerts_deque)
# - Manual event buffering into 5-second windows
# - Callback-style batch processing
# - Window latency tracking in seconds
# - Aggregated metrics per window
```

## 📱 Dashboard Modes

- **Both**: Side-by-side panels for direct comparison ← **Recommended for presentations**
- **Reactive**: Full focus on reactive paradigm
- **Traditional**: Full focus on traditional paradigm

## 🎬 Presentation Tips

1. **Start with "Both" mode** - visual comparison is most impactful
2. **Let simulation run for 10-15 seconds** - wait for first traditional window to close
3. **Screenshot key moments**:
   - First high-temp event: notice Reactive alerts immediately
   - Traditional catches up in next 5-second window
   - Latency metrics show the stark difference (50ms vs 5000ms)
4. **Adjust simulation speed to 2.0x** for faster demo time

## 🛠️ Technologies

- **Streamlit**: Interactive web dashboard
- **RxPY**: Reactive extensions for Python (event streams)
- **Pandas**: Data manipulation and aggregation
- **Python 3.8+**: Language version

## 📚 Paradigm Comparison

| Aspect | Traditional | Reactive |
|--------|-----------|----------|
| **Processing** | Batch / Windowed | Event-driven / Stream |
| **Latency** | ~5 seconds | <100ms |
| **Code Style** | Callbacks + Threading | Observable chains |
| **State Management** | Manual (queues, locks) | Automatic (operators) |
| **Responsiveness** | Delayed | Immediate |
| **Use Case** | Analytics, Reports | Real-time, IoT, Alerts |

## 🤝 Contributing

This project demonstrates **best practices** for:
- Reactive stream programming in Python
- Event-driven system design
- Paradigm comparison through interactive visualization
- Clear presentation of complex concepts

## 📝 Notes

- **Legacy files** (`main.py`, `visualization.py`) are kept for reference but superseded by the dashboard
- Core logic consolidated in `core/` for maintainability
- Dashboard is the primary demo mechanism for presentations
- All performance metrics are tracked and visible in the UI
