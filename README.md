# Weather CLI

A Python command-line tool that fetches and displays weather data beautifully in the terminal. Uses the [Open-Meteo API](https://open-meteo.com/) (free, no API key required) and [Rich](https://github.com/Textualize/rich) for colorful formatting.

![Python](https://img.shields.io/badge/python-3.8+-blue)

## Features

- Current weather conditions (temperature, humidity, wind, etc.)
- 5-day forecast with high/low temps, precipitation, sunrise/sunset
- Celsius (default) or Fahrenheit output
- Weather emojis and color-coded display
- Works with any city worldwide

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

## Usage

```bash
python weather.py <city>            # Current weather + 5-day forecast (Celsius)
python weather.py <city> -f         # Use Fahrenheit
python weather.py "New York" -f     # Multi-word city names
python weather.py --help            # Show usage
```

## Example

```
$ python weather.py London

Fetching weather for London...

┌───────── Current Weather: London, England, United Kingdom ──────────┐
│                                                                     │
│                              🌧️                                     │
│                                                                     │
│      Temperature:    8.7°C                                          │
│       Feels like:    6.8°C                                          │
│         Humidity:    89%                                             │
│             Wind:    7.4 km/h SSE                                   │
│       Conditions:    🌧️  Slight rain                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌────────────────────────── 5-Day Forecast ───────────────────────────┐
│ Date       Conditions              High     Low    Precip  ...      │
│ Mon 02/09  🌦️ Slight rain showers  11.5°C   7.3°C  2.6 mm  ...     │
│ Tue 02/10  🌦️ Slight rain showers  12.6°C   8.6°C  4.2 mm  ...     │
│ Wed 02/11  🌧️ Slight rain          12.3°C   8.3°C  2.7 mm  ...     │
│ ...                                                                 │
└─────────────────────────────────────────────────────────────────────┘
```

## Dependencies

- [requests](https://docs.python-requests.org/) — HTTP client
- [rich](https://rich.readthedocs.io/) — Terminal formatting

## API

Weather data provided by [Open-Meteo](https://open-meteo.com/) — free for non-commercial use, no API key needed.
