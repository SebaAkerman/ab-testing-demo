import requests

BASE = "http://localhost:5000"

scenarios = [
    {"variant": "A", "visits": 50, "conv_rate": 0.20, "avg_seconds": 30},
    {"variant": "B", "visits": 50, "conv_rate": 0.40, "avg_seconds": 20},
]

for s in scenarios:
    clicks = int(s["visits"] * s["conv_rate"])
    payload = {
        "variant": s["variant"],
        "visits": s["visits"],
        "clicks": clicks,
        "avg_seconds": s["avg_seconds"],
    }
    resp = requests.post(f"{BASE}/simulate", json=payload)
    resp.raise_for_status()
    print(f"Variant {s['variant']}: {resp.json()}")
