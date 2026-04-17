import time
import threading

# ====================== MAIN MENU ======================
def main():
    print("=" * 70)
    print("   Paradigmes de Langages de Programmation - Projet Final")
    print("   Reactive Programming (RxPY) vs Traditional Callbacks")
    print("   IoT Sensor Management (Motion + Temperature)")
    print("=" * 70)
    print()

    while True:
        print("Choose an option:")
        print("1. Traditional approach only (callback + threading)")
        print("2. Reactive approach only (console output)")
        print("3. Both approaches (console comparison)")
        print("4. Reactive + LIVE VISUALIZATION (Best for demo & report)")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            print("\n" + "="*60)
            from traditional_callback import run_traditional
            run_traditional()
            print("="*60)

        elif choice == "2":
            print("\n" + "="*60)
            run_reactive_console()
            print("="*60)

        elif choice == "3":
            print("\n" + "="*60)
            run_both_console()
            print("="*60)

        elif choice == "4":
            print("\n" + "="*60)
            run_reactive_with_visualization()
            print("="*60)
            break  # visualization blocks until window is closed

        elif choice == "5":
            print("\nThank you! Good luck with your presentation.")
            break

        else:
            print("Invalid choice. Please try again.\n")


# ====================== REACTIVE CONSOLE ONLY ======================
def run_reactive_console():
    """Run Reactive approach with console output only"""
    print("=== Starting REACTIVE approach (Console) with RxPY ===\n")

    from reactive_pipeline import create_reactive_pipeline

    processed_pipeline, _ = create_reactive_pipeline()   # We only need processed here

    def on_next(result):
        print(f"[REACTIVE WINDOW] {result['window_end']} → "
              f"Motion: {result['motion_detections']} | "
              f"High Temp: {result['high_temp_readings']} | "
              f"Avg Temp: {result['avg_temp']}°C | "
              f"Total alerts: {result['total_alerts']}")

    def on_error(err):
        print(f"[REACTIVE] Error: {err}")

    subscription = processed_pipeline.subscribe(on_next=on_next, on_error=on_error)

    try:
        print("Running for 30 seconds... (Press Ctrl+C to stop)\n")
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        subscription.dispose()
        print("\n=== Reactive console mode stopped ===\n")


# ====================== BOTH CONSOLE ======================
def run_both_console():
    """Run both Traditional and Reactive side by side (console)"""
    print("=== Running BOTH approaches simultaneously (Console) ===\n")
    print("Watch the difference in code style and output cleanliness.\n")

    stop_event = threading.Event()

    # Traditional in a background thread
    def run_traditional_thread():
        from traditional_callback import run_traditional
        run_traditional()

    trad_thread = threading.Thread(target=run_traditional_thread, daemon=True)
    trad_thread.start()

    time.sleep(1.5)  # Small delay to separate outputs

    # Reactive
    from reactive_pipeline import create_reactive_pipeline
    processed_pipeline, _ = create_reactive_pipeline()

    def on_next(result):
        print(f"[REACTIVE WINDOW] {result['window_end']} → "
              f"Motion: {result['motion_detections']} | "
              f"High Temp: {result['high_temp_readings']} | "
              f"Avg Temp: {result['avg_temp']}°C")

    subscription = processed_pipeline.subscribe(on_next=on_next)

    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nDemo stopped.")
    finally:
        subscription.dispose()
        stop_event.set()
        print("\n=== Both approaches finished ===\n")


# ====================== REACTIVE + LIVE VISUALIZATION ======================
def run_reactive_with_visualization():
    """Reactive approach with real-time matplotlib visualization (Recommended)"""
    print("=== Starting REACTIVE approach WITH LIVE VISUALIZATION ===\n")
    print("A plot window will open showing live temperature and motion events.")
    print("Close the plot window to stop the demo.\n")

    from reactive_pipeline import create_reactive_pipeline
    from visualization import start_visualization

    # Get both pipelines: processed (for console) + raw (for visualization)
    processed_pipeline, raw_merged = create_reactive_pipeline()

    # Console aggregated windows
    def on_next(result):
        print(f"[REACTIVE WINDOW] {result['window_end']} → "
              f"Motion: {result['motion_detections']} | "
              f"High Temp: {result['high_temp_readings']} | "
              f"Avg Temp: {result['avg_temp']}°C")

    processed_pipeline.subscribe(on_next=on_next)

    # Start live visualization (this will block until plot is closed)
    start_visualization(raw_merged)


if __name__ == "__main__":
    main()