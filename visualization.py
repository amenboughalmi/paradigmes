import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# Data buffers
temp_times = deque(maxlen=200)
temp_values = deque(maxlen=200)
motion_times = deque(maxlen=100)

# Create figure
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)
fig.suptitle('IoT Reactive System - Live Visualization (RxPY)', fontsize=16, fontweight='bold')

# === Temperature Plot ===
line_temp, = ax1.plot([], [], 'b-', linewidth=2.8, label='Temperature (°C)')
ax1.set_ylabel('Temperature (°C)', fontsize=12)
ax1.set_ylim(15, 35)
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.4)

# === Motion Plot ===
ax2.set_ylabel('Motion Detected', fontsize=12)
ax2.set_ylim(0, 6)
ax2.grid(True, alpha=0.4)

def init():
    line_temp.set_data([], [])
    return line_temp,

def update(frame):
    current_time = time.time()

    # Update Temperature
    if temp_times:
        line_temp.set_data(list(temp_times), list(temp_values))
        ax1.relim()
        ax1.autoscale_view(scalex=False, scaley=False)

    # Update Motion (red vertical lines)
    ax2.clear()
    ax2.set_ylabel('Motion Detected', fontsize=12)   # Restore label every time
    ax2.set_ylim(0, 6)
    ax2.grid(True, alpha=0.4)

    for t in motion_times:
        ax2.axvline(x=t, ymin=0, ymax=0.85, color='red', linewidth=3.2, alpha=0.9)

    # Scroll x-axis (last 50 seconds)
    ax1.set_xlim(current_time - 50, current_time)
    ax2.set_xlim(current_time - 50, current_time)

    return line_temp,


def start_visualization(raw_observable=None):
    """Start live visualization"""
    global ani

    print("🎥 Live visualization starting... (Close the plot window to stop)\n")

    def on_next(data):
        current_t = time.time()

        if data.get("sensor") == "temperature":
            temp_times.append(current_t)
            temp_values.append(data.get("value", 0))

        elif data.get("sensor") == "motion" and data.get("value") == 1:
            motion_times.append(current_t)

    # Subscribe to raw sensor data
    if raw_observable:
        raw_observable.subscribe(on_next=on_next)

    # Start animation
    ani = FuncAnimation(
        fig, 
        update, 
        init_func=init,
        interval=180,          # Balanced refresh rate
        blit=False,
        cache_frame_data=False
    )

    plt.tight_layout()
    plt.show(block=True)
    print("\nVisualization window closed.")