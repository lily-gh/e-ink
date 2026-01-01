# weather_example.py
import os, requests, datetime

KEY = os.getenv("OPENWEATHER_KEY")  # set in /etc/environment or systemd service
lat, lon = 52.483333, 13.366667      # Schöneberg approx

url = "https://api.openweathermap.org/data/3.0/onecall"
params = {
    "lat": lat,
    "lon": lon,
    "exclude": "minutely",   # keep hourly+daily+alerts if you want
    "units": "metric",
    "appid": KEY
}

r = requests.get(url, params=params, timeout=10)
r.raise_for_status()
data = r.json()

# current weather
current_temp = int(data["current"]["temp"])
current_desc = data["current"]["weather"][0]["description"]

# today min/max (first daily entry)
today = data["daily"][0]
min_temp = int(today["temp"]["min"])
max_temp = int(today["temp"]["max"])

# next 5 days forecast (date, min, max, short desc)
forecast = []
for d in data["daily"][1:6]:
    dt = datetime.datetime.fromtimestamp(d["dt"]).date().isoformat()
    forecast.append({
        "date": dt,
        "min": int(d["temp"]["min"]),
        "max": int(d["temp"]["max"]),
        "desc": d["weather"][0]["description"]
    })

# Create JSON output
import json
output = {
    "now": {
        "temp": current_temp,
        "desc": current_desc,
        "min": min_temp,
        "max": max_temp
    },
    "forecast": forecast
}

print(json.dumps(output, indent=2))

