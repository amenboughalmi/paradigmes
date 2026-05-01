"""
Shared configuration for the Reactive vs Traditional comparison project.
"""

# Temperature Threshold
HIGH_TEMP_THRESHOLD = 21.0

# Dashboard settings
MAX_POINTS = 160          # Max data points to keep in memory
WINDOW_SECONDS = 5.0      # Traditional aggregation window size

# Simulation settings
MOTION_SENSOR_INTERVAL = (0.5, 1.5)      # seconds
TEMPERATURE_SENSOR_INTERVAL = (1.0, 2.0)  # seconds
TEMPERATURE_FLUCTUATION = (-0.5, 0.5)     # degree change per reading
TEMPERATURE_MIN = 17.0
TEMPERATURE_MAX = 26.5
TEMPERATURE_INITIAL = 20.0
