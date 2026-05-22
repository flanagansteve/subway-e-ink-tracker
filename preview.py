"""
Mac preview script — fetches live data from the active API, renders the display
image, and saves it to preview.png. Open that file to see the layout.

Usage:
    .venv/bin/python3 preview.py
"""
import subprocess
import sys
from datetime import datetime

from config import config
from subway_service import subway_service, TransitService
from weather_service import weather_service
from layout import getImage

api_name = "Transit" if isinstance(subway_service, TransitService) else "MBTA"
print(f"[{api_name} API] Fetching transit data...")
trains = subway_service.get_upcoming_trains()
print(f"  Got {len(trains)} arrivals")

print("Fetching weather...")
weather_data = weather_service.get_weather()
if not weather_data:
    print("  Warning: no weather data, using placeholder")
    weather_data = {
        "current": {
            "temperature": "65",
            "condition_code": 113,
            "conditions": "Clear",
            "wind_mph": 5,
            "precipitation_chance": 0,
        },
        "hourly": [],
        "daily": {},
    }
else:
    print("  Weather OK")

print("Rendering image...")
img = getImage(weather_data, trains)

out = "preview.png"
img.save(out)
print(f"Saved to {out}  ({img.size[0]}x{img.size[1]})")

# Open the image automatically on Mac
subprocess.run(["open", out])
