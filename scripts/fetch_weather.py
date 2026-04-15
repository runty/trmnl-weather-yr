#!/usr/bin/env python3
"""Fetch weather from Yr.no API and generate flat JSON for TRMNL."""

import json
import math
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen

YR_BASE = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
USER_AGENT = "TRMNL-Weather-Yr/1.0 github.com/runty"

SYMBOL_TO_WI = {
    "clearsky_day": ("wi-day-sunny", False),
    "clearsky_night": ("wi-night-clear", False),
    "fair_day": ("wi-day-sunny", False),
    "fair_night": ("wi-night-clear", False),
    "partlycloudy_day": ("wi-day-cloudy", False),
    "partlycloudy_night": ("wi-night-alt-partly-cloudy", False),
    "cloudy": ("wi-cloudy", False),
    "fog": ("wi-fog", False),
    "lightrainshowers_day": ("wi-day-sprinkle", True),
    "lightrainshowers_night": ("wi-night-alt-sprinkle", True),
    "rainshowers_day": ("wi-day-rain", True),
    "rainshowers_night": ("wi-night-alt-rain", True),
    "heavyrainshowers_day": ("wi-rain", True),
    "heavyrainshowers_night": ("wi-rain", True),
    "lightrain": ("wi-day-sprinkle", True),
    "rain": ("wi-day-rain", True),
    "heavyrain": ("wi-rain", True),
    "lightsnowshowers_day": ("wi-day-snow", True),
    "lightsnowshowers_night": ("wi-night-alt-snow", True),
    "snowshowers_day": ("wi-day-snow", True),
    "snowshowers_night": ("wi-night-alt-snow", True),
    "heavysnowshowers_day": ("wi-snow", True),
    "heavysnowshowers_night": ("wi-snow", True),
    "lightsnow": ("wi-day-snow", True),
    "snow": ("wi-day-snow", True),
    "heavysnow": ("wi-snow", True),
    "lightssleetshowers_day": ("wi-day-rain-mix", True),
    "sleetshowers_day": ("wi-day-rain-mix", True),
    "lightsleet": ("wi-day-rain-mix", True),
    "sleet": ("wi-day-rain-mix", True),
    "lightrainandthunder": ("wi-day-thunderstorm", True),
    "rainandthunder": ("wi-day-thunderstorm", True),
    "heavyrainandthunder": ("wi-thunderstorm", True),
    "lightsnowandthunder": ("wi-day-snow-thunderstorm", True),
    "snowandthunder": ("wi-day-snow-thunderstorm", True),
    "lightrainshowersandthunder_day": ("wi-day-thunderstorm", True),
    "rainshowersandthunder_day": ("wi-day-thunderstorm", True),
    "heavyrainshowersandthunder_day": ("wi-thunderstorm", True),
    "lightrainshowersandthunder_night": ("wi-night-alt-thunderstorm", True),
    "rainshowersandthunder_night": ("wi-night-alt-thunderstorm", True),
}


def fetch_json(url):
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def deg_to_compass(deg):
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = round(deg / 45) % 8
    return dirs[idx]


def map_symbol(code):
    if code in SYMBOL_TO_WI:
        return SYMBOL_TO_WI[code]
    # Fuzzy match
    for key, val in SYMBOL_TO_WI.items():
        if key in code or code in key:
            return val
    return ("wi-cloud", False)


def parse_timeseries(ts_list):
    """Parse Yr.no timeseries into hourly and daily data."""
    hourly = []
    for ts in ts_list[:24]:
        instant = ts["data"]["instant"]["details"]
        n1 = ts["data"].get("next_1_hours", {})
        n6 = ts["data"].get("next_6_hours", {})
        sym_code = n1.get("summary", {}).get("symbol_code", "") or n6.get("summary", {}).get("symbol_code", "")
        precip = n1.get("details", {}).get("precipitation_amount", 0) or 0
        wi_class, is_precip = map_symbol(sym_code)

        hourly.append({
            "time_iso": ts["time"],
            "temp": round(instant.get("air_temperature", 0)),
            "icon": wi_class,
            "is_precip": is_precip,
            "precip_mm": precip,
            "precip_bar": min(round(precip * 20), 100),
            "wind_speed": round(instant.get("wind_speed", 0) * 3.6),
            "wind_dir": deg_to_compass(instant.get("wind_from_direction", 0)),
            "humidity": round(instant.get("relative_humidity", 0)),
            "symbol": sym_code,
        })

    # Daily: pick noon entries
    daily = []
    seen_days = set()
    for ts in ts_list:
        dt = datetime.fromisoformat(ts["time"].replace("Z", "+00:00"))
        day_key = dt.strftime("%Y-%m-%d")
        if dt.hour == 12 and day_key not in seen_days:
            instant = ts["data"]["instant"]["details"]
            n6 = ts["data"].get("next_6_hours", {})
            n12 = ts["data"].get("next_12_hours", {})
            sym_code = n6.get("summary", {}).get("symbol_code", "") or n12.get("summary", {}).get("symbol_code", "")
            wi_class, is_precip = map_symbol(sym_code)

            daily.append({
                "day": dt.strftime("%a"),
                "date": day_key,
                "high": round(instant.get("air_temperature", 0)),
                "icon": wi_class,
                "is_precip": is_precip,
                "symbol": sym_code,
            })
            seen_days.add(day_key)
            if len(daily) >= 7:
                break

    # Get overnight lows (midnight entries)
    for ts in ts_list:
        dt = datetime.fromisoformat(ts["time"].replace("Z", "+00:00"))
        day_key = dt.strftime("%Y-%m-%d")
        if dt.hour == 0:
            for d in daily:
                if d["date"] == day_key:
                    d["low"] = round(ts["data"]["instant"]["details"].get("air_temperature", 0))

    return hourly, daily


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "api")
    os.makedirs(out_dir, exist_ok=True)

    lat = float(os.environ.get("WEATHER_LAT", "49.154"))
    lon = float(os.environ.get("WEATHER_LON", "-123.158"))

    url = f"{YR_BASE}?lat={lat}&lon={lon}"
    data = fetch_json(url)

    ts_list = data["properties"]["timeseries"]
    hourly, daily_forecast = parse_timeseries(ts_list)

    # Current conditions from first entry
    first = ts_list[0]
    cur = first["data"]["instant"]["details"]
    cur_sym = (first["data"].get("next_1_hours", {}).get("summary", {}).get("symbol_code", "")
               or first["data"].get("next_6_hours", {}).get("summary", {}).get("symbol_code", ""))
    wi_class, is_precip = map_symbol(cur_sym)

    condition = cur_sym.replace("_", " ").replace("day", "").replace("night", "").strip().title()

    result = {
        "current": {
            "temp": round(cur.get("air_temperature", 0)),
            "condition": condition,
            "icon": wi_class,
            "is_precip": is_precip,
            "wind_speed": round(cur.get("wind_speed", 0) * 3.6),
            "wind_dir": deg_to_compass(cur.get("wind_from_direction", 0)),
            "humidity": round(cur.get("relative_humidity", 0)),
            "symbol": cur_sym,
        },
        "hourly": hourly,
        "daily": daily_forecast,
        "lat": lat,
        "lon": lon,
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }

    path = os.path.join(out_dir, "weather.json")
    with open(path, "w") as f:
        json.dump(result, f, separators=(",", ":"))

    print(f"Location: {lat}, {lon}")
    print(f"Current: {result['current']['temp']}°C {result['current']['condition']}")
    print(f"Hourly: {len(hourly)} hours")
    print(f"Daily: {len(daily_forecast)} days")
    print(f"Done. Written to {path}")


if __name__ == "__main__":
    main()
