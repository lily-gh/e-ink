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
current_temp = data["current"]["temp"]
current_desc = data["current"]["weather"][0]["description"]

# today min/max (first daily entry)
today = data["daily"][0]
min_temp = today["temp"]["min"]
max_temp = today["temp"]["max"]

# next 3 days forecast (date, min, max, short desc)
forecast = []
for d in data["daily"][1:4]:
    dt = datetime.datetime.fromtimestamp(d["dt"]).date().isoformat()
    forecast.append({"date": dt, "min": d["temp"]["min"], "max": d["temp"]["max"],
                     "desc": d["weather"][0]["description"]})

print("Now:", current_temp, current_desc)
print("Today min/max:", min_temp, max_temp)
print("Next days:", forecast)

