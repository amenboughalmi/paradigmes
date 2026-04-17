import time
import queue
import threading
from sensors import motion_sensor, temperature_sensor

# Global shared queue + locks (typical in traditional approach)
data_queue = queue.Queue()
stop_event = threading.Event()

# ==================== CALLBACKS ====================
def process_motion(data):
    """Callback for motion sensor data"""
    if data["value"] == 1:
        print(f"[TRADITIONAL] MOTION DETECTED at {time.strftime('%H:%M:%S', time.localtime(data['timestamp']))}")
        # In real code, you might call another function here → nesting starts


def process_temperature(data):
    """Callback for temperature sensor data"""
    if data["value"] > 25.0:
        print(f"[TRADITIONAL] HIGH TEMPERATURE ALERT: {data['value']}°C")


def aggregator_callback():
    """This simulates aggregation (count motion + average temp) – becomes messy fast"""
    motion_count = 0
    temps = []
    last_window = time.time()

    while not stop_event.is_set():
        try:
            data = data_queue.get(timeout=0.5)
            if data["sensor"] == "motion" and data["value"] == 1:
                motion_count += 1
            elif data["sensor"] == "temperature":
                temps.append(data["value"])

            # Every 5 seconds, show aggregated result
            if time.time() - last_window >= 5.0:
                avg_temp = sum(temps) / len(temps) if temps else 0
                print(f"[TRADITIONAL] 5s WINDOW → Motion events: {motion_count} | Avg Temp: {avg_temp:.2f}°C")
                motion_count = 0
                temps.clear()
                last_window = time.time()

        except queue.Empty:
            continue
        except Exception as e:
            print(f"[TRADITIONAL] Error in aggregator: {e}")


# ==================== SENSOR THREADS ====================
def run_sensor(generator, callback):
    """Run a sensor generator and call callback on each value"""
    for data in generator():
        if stop_event.is_set():
            break
        try:
            callback(data)
            data_queue.put(data)          # also send to aggregator
        except Exception as e:
            print(f"Error in sensor callback: {e}")


# ==================== MAIN ====================
def run_traditional():
    print("=== Starting TRADITIONAL callback + threading approach ===\n")

    # Start aggregator thread
    agg_thread = threading.Thread(target=aggregator_callback, daemon=True)
    agg_thread.start()

    # Start motion sensor thread
    motion_thread = threading.Thread(
        target=run_sensor,
        args=(motion_sensor, process_motion),
        daemon=True
    )
    motion_thread.start()

    # Start temperature sensor thread
    temp_thread = threading.Thread(
        target=run_sensor,
        args=(temperature_sensor, process_temperature),
        daemon=True
    )
    temp_thread.start()

    try:
        time.sleep(25)   # Run for 25 seconds
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        print("\n=== Traditional approach stopped ===\n")


if __name__ == "__main__":
    run_traditional()