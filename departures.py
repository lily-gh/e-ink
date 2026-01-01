import requests
from datetime import datetime

BASE = "https://v6.bvg.transport.rest"
STOP_ID = "900058105"  # Lindenhof
LINE_NAME = "106"
DURATION_MIN = 45

resp = requests.get(
    f"{BASE}/stops/{STOP_ID}/departures",
    params={"duration": DURATION_MIN},
    timeout=10
)
resp.raise_for_status()

departures = resp.json().get("departures", [])

results = []
for dep in departures:
    if dep.get("line", {}).get("name") != LINE_NAME:
        continue

    when = dep.get("when") or dep.get("plannedWhen")
    direction = dep.get("direction", "Unknown")
    delay = dep.get("delay", 0)

    if when:
        t = datetime.fromisoformat(when.replace("Z", "+00:00"))
        results.append({
            "time": t.strftime("%H:%M"),
            "direction": direction,
            "delay_min": delay // 60 if delay else 0
        })

print("Bus 106 @ Lindenhof:")
for r in results[:4]:
    delay = f" (+{r['delay_min']} min)" if r["delay_min"] else ""
    print(f"- {r['time']} → {r['direction']}{delay}")

# Return as JSON array sorted by departure time
import json
output = [{"time": r["time"], "direction": r["direction"]} for r in results[:3]]
print("\nDepartures as JSON array:")
print(json.dumps(output, ensure_ascii=False))
