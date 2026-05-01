# Reactive vs Traditional IoT Dashboard

An interactive **Streamlit dashboard** that provides a real-time, side-by-side comparison of two programming paradigms:

## Paradigm Comparison

### 🕐 Traditional (Windowed, Batch Processing)
- Events aggregated into **5-second windows**
- **Delayed processing** until window closes
- Average latency: **~2.5-5 seconds**
- Useful for: Reports, analytics, backpressure handling
- Visual indicator: Orange dividers, clock emoji (🕐)

### ⚡ Reactive (Event-Driven, Immediate)
- Events processed **immediately** upon arrival
- **Low-latency response** with millisecond responsiveness
- Average latency: **<100ms** (tracked per event)
- Useful for: Real-time control systems, IoT alerts, critical actions
- Visual indicator: Green dividers, lightning emoji (⚡)

## Key Features

✨ **Live Metrics**
- Current temperature, motion alerts, high-temp alerts
- **Latency indicators** showing response times
- Traditional: seconds (window delay)
- Reactive: milliseconds (event response)

📊 **Side-by-Side Visualization**
- Run both paradigms simultaneously in split view
- Or view individually (Traditional or Reactive only)
- Real-time charts for temperature trends
- Event-based charts for alerts

🎛️ **Interactive Controls**
- Mode selector (Traditional / Reactive / Both)
- Temperature threshold slider
- Simulation speed control (0.5x to 3.0x)
- Start / Stop / Reset buttons
- Live status indicator

📢 **Color-Coded Alert Feed**
- ⚡ Reactive alerts in real-time
- 🕐 Traditional alerts after window closes
- Sorted by most recent (LIFO)
- Shows latency metrics for comparison

## Running the Dashboard

```bash
# Navigate to project directory
cd c:\School\GitHub\paradigmes#

# Run the Streamlit app
streamlit run dashboard/dashboard_app.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Project Structure

```
paradigmes#/
├── core/                    # Shared core modules
│   ├── __init__.py
│   ├── config.py           # Shared configuration
│   ├── sensors.py          # IoT sensor simulators
│   └── engines.py          # Reactive & Traditional engines
├── dashboard/              # Streamlit dashboard
│   ├── dashboard_app.py    # Main dashboard application
│   ├── config.py           # Dashboard config (imports from core)
│   └── README.md           # This file
├── main.py                 # (Deprecated: use dashboard instead)
└── README.md               # Project overview
```

## Engine Classes

### ReactiveEngine
- Uses RxPY `Subject` for reactive stream processing
- Immediate event subscription with low latency
- Tracks individual temperature and motion events
- Performance metrics: event latency in milliseconds

### TraditionalEngine
- Manual event buffering into 5-second windows
- Callback-style batch processing
- Aggregates metrics (average temp, event counts)
- Performance metrics: window delay in seconds

Both engines share the same alert feed for comparison.

## Presentation Tips for Screenshots

1. **Run in "Both" mode** for maximum impact
   - Side-by-side comparison clearly shows the paradigm difference
   - Wait for first 5-second window to close in Traditional (watch the latency!)
   - Reactive immediately shows events

2. **Temperature Threshold Slider**
   - Set to ~21°C to see high-temp alerts
   - Adjust simulation speed to 2.0x for faster demo

3. **Alert Feed**
   - Shows the latency difference clearly
   - Reactive alerts appear instantly (<50ms typically)
   - Traditional alerts batch after 5 seconds

4. **Latency Metrics**
   - Compare the "Latency" indicators in the metrics
   - Reactive: milliseconds
   - Traditional: seconds (full window cycle)

## Technologies Used

- **Streamlit**: Interactive dashboard framework
- **RxPY**: Reactive extensions for Python
- **Pandas**: Data manipulation and visualization
- **Python 3.8+**

## Authors & Contributions

This project demonstrates reactive programming paradigm in Python for a programming language course project.
