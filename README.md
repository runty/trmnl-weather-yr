# TRMNL Global Weather Forecast (Yr.no)

A TRMNL recipe showing current conditions, 24-hour hourly forecast with precipitation bars and mm amounts, and 7-day forecast. Data from Yr.no (Norwegian Meteorological Institute) — works for any location worldwide.

## Features

- **Current conditions** — temperature, condition, wind speed/direction, humidity
- **24-hour hourly forecast** — 3 columns x 8 rows with time, icon, temp, precipitation bar + mm amount
- **7-day daily forecast** — day name, icon, high/low temperatures
- **Weather Icons font** ([erikflowers/weather-icons](https://github.com/erikflowers/weather-icons)) — 222 scalable vector icons, blue for clear, red for precipitation
- **Global coverage** — any coordinates worldwide (Yr.no covers the entire globe)
- **Precipitation bars** — blue (rain amount) / yellow (dry) based on mm forecast
- Data updated **hourly** via GitHub Actions

## Setup

### 1. Fork this repository

### 2. Set your coordinates
Edit `.github/workflows/update-data.yml` and change `WEATHER_LAT` and `WEATHER_LON`:
```yaml
env:
  WEATHER_LAT: "49.154"
  WEATHER_LON: "-123.158"
```

### 3. Enable GitHub Pages
Settings > Pages > Source: **GitHub Actions**

### 4. Run the data fetch
Actions > "Update Weather Data" > Run workflow

### 5. Create a Private Plugin on TRMNL
1. Plugins > Private Plugin
2. Strategy: **Polling**
3. Polling URL: `https://YOUR_USERNAME.github.io/trmnl-weather-yr/weather.json`
4. Paste `form_fields.yml` into Custom Fields
5. Paste templates into markup tabs (shared, full, half horizontal, half vertical, quadrant)
6. Save and **Force Refresh**

## Layouts

### Full (800x480)
Current conditions + 6-day forecast at top. 24-hour hourly in 3 columns below with precipitation bars and mm amounts.

### Half Horizontal (800x240)
Current conditions left, 7-day forecast right.

### Half Vertical (400x480)
18-hour hourly forecast with precipitation bars.

### Quadrant (400x240)
Current conditions + 4-day forecast.

## Project Structure

```
trmnl-weather-yr/
├── .github/workflows/
│   ├── pages.yml              # Deploy to GitHub Pages
│   └── update-data.yml        # Fetch weather hourly
├── api/
│   └── weather.json           # Generated flat JSON
├── scripts/
│   └── fetch_weather.py       # Yr.no API fetcher + transformer
├── templates/
│   ├── shared.liquid          # Fonts, CSS, Weather Icons
│   ├── full.liquid            # Current + daily + 24h hourly
│   ├── half_horizontal.liquid # Current + 7-day
│   ├── half_vertical.liquid   # 18-hour hourly
│   └── quadrant.liquid        # Current + 4-day
├── form_fields.yml            # Author bio
├── settings.yml               # Plugin metadata
└── README.md
```

## Data Source

Yr.no / MET Norway (`api.met.no`). Free, global, Creative Commons licensed. Python script transforms Yr.no's nested timeseries JSON into flat structure for TRMNL's Liquid templates.

## Technical Notes

- Yr.no symbol codes (e.g. `clearsky_day`, `lightrainshowers_night`) mapped to Weather Icons classes
- Wind converted from m/s to km/h, degrees to compass direction
- Precipitation bars scale: 1mm = 20% bar width (5mm = 100%)
- Daily forecast extracted from noon (12:00 UTC) timeseries entries
- Overnight lows from midnight (00:00 UTC) entries
