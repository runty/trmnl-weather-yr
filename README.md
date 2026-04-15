# TRMNL Global Weather Forecast (Yr.no)

A TRMNL recipe showing current conditions, 24-hour hourly forecast with precipitation bars, and 6-day forecast. Data from Yr.no (Norwegian Meteorological Institute) — works for any location worldwide. No server needed.

## Features

- **Current conditions** — temperature, condition, wind speed/direction, humidity
- **24-hour hourly forecast** — 3 columns x 8 rows with time, icon, temp, precipitation bar
- **6-day daily forecast** — day name, icon, high temperature
- **Weather Icons font** — 222 scalable vector icons, blue for clear, red for precipitation
- **Global coverage** — any coordinates worldwide
- **Direct API polling** — TRMNL polls Yr.no API directly, no GitHub Pages/Actions needed
- **Precipitation bars** — blue (rain amount) / yellow (dry) based on mm forecast
- Refreshes **every hour**

## Setup

### 1. Create a Private Plugin on TRMNL
1. Plugins > Private Plugin
2. Strategy: **Polling**
3. Polling URL: `https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={{latitude}}&lon={{longitude}}`
4. Polling Headers: `User-Agent=TRMNL-Weather-Yr/1.0 github.com/runty`
5. Paste `form_fields.yml` into Custom Fields
6. Enter your latitude and longitude (default: Richmond BC)
7. Paste templates into markup tabs
8. Save and **Force Refresh**

## Layouts

### Full (800x480)
Current conditions + 6-day forecast at top. 24-hour hourly in 3 columns below with precipitation bars.

### Half Horizontal (800x240)
Current conditions left, 7-day forecast right.

### Half Vertical (400x480)
18-hour hourly forecast with precipitation bars.

### Quadrant (400x240)
Current conditions + 4-day forecast.

## Data Source

Yr.no / MET Norway (`api.met.no`). Free, global, Creative Commons licensed. Requires User-Agent header. Hourly for 48-72h, then 6-hourly for 9-10 days.
