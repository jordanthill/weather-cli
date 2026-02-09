"""Weather CLI Tool — Fetch and display weather data beautifully in the terminal."""

import argparse
import os
import sys
from datetime import datetime

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

__version__ = "1.0.0"

# API endpoints
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# WMO Weather Code → (description, emoji)
WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Light freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌧️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Light freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snowfall", "❄️"),
    73: ("Moderate snowfall", "❄️"),
    75: ("Heavy snowfall", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌦️"),
    82: ("Violent rain showers", "🌧️"),
    85: ("Slight snow showers", "❄️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with slight hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}

CARDINAL_DIRECTIONS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
]


# --- API Functions ---

def geocode_city(city_name):
    """Convert a city name to geographic coordinates using Open-Meteo geocoding API."""
    try:
        response = requests.get(
            GEOCODING_URL,
            params={"name": city_name, "count": 5},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if "results" not in data or not data["results"]:
            return None

        result = data["results"][0]
        return {
            "name": result.get("name", city_name),
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "country": result.get("country", ""),
            "admin1": result.get("admin1", ""),
        }
    except requests.RequestException as e:
        print(f"[red]Error connecting to geocoding service: {e}[/red]")
        return None


def fetch_weather(lat, lon, use_fahrenheit=False):
    """Fetch current weather and forecast from Open-Meteo API."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "weather_code",
            "wind_speed_10m",
            "wind_direction_10m",
        ]),
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "weather_code",
            "precipitation_sum",
            "sunrise",
            "sunset",
        ]),
        "timezone": "auto",
        "forecast_days": 5,
    }

    if use_fahrenheit:
        params["temperature_unit"] = "fahrenheit"
        params["wind_speed_unit"] = "mph"

    try:
        response = requests.get(WEATHER_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[red]Error fetching weather data: {e}[/red]")
        return None


# --- Formatting Helpers ---

def get_weather_icon(code):
    """Get the emoji icon for a WMO weather code."""
    if code in WEATHER_CODES:
        return WEATHER_CODES[code][1]
    return "🌡️"


def get_weather_description(code):
    """Get the text description for a WMO weather code."""
    if code in WEATHER_CODES:
        return WEATHER_CODES[code][0]
    return "Unknown"


def format_temperature(temp, use_fahrenheit):
    """Format a temperature value with unit symbol."""
    unit = "°F" if use_fahrenheit else "°C"
    return f"{temp:.1f}{unit}"


def format_wind(speed, direction_degrees, use_fahrenheit):
    """Format wind speed and direction as a readable string."""
    unit = "mph" if use_fahrenheit else "km/h"
    index = round(direction_degrees / 22.5) % 16
    cardinal = CARDINAL_DIRECTIONS[index]
    return f"{speed:.1f} {unit} {cardinal}"


def format_time(iso_str):
    """Parse an ISO 8601 datetime string and return a 12-hour time like '6:45 AM'."""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%-I:%M %p") if sys.platform != "win32" else dt.strftime("%#I:%M %p")
    except (ValueError, TypeError):
        return iso_str


# --- Display Functions ---

def display_current_weather(location, weather, use_fahrenheit, console):
    """Display current weather conditions in a Rich panel."""
    current = weather["current"]
    code = current.get("weather_code", 0)
    icon = get_weather_icon(code)
    description = get_weather_description(code)

    location_parts = [location["name"]]
    if location.get("admin1"):
        location_parts.append(location["admin1"])
    if location.get("country"):
        location_parts.append(location["country"])
    title = ", ".join(location_parts)

    table = Table(show_header=False, show_edge=False, box=None, padding=(0, 2))
    table.add_column("Label", style="cyan", justify="right", min_width=14)
    table.add_column("Value", style="white")

    table.add_row("Temperature:", format_temperature(current["temperature_2m"], use_fahrenheit))
    table.add_row("Feels like:", format_temperature(current["apparent_temperature"], use_fahrenheit))
    table.add_row("Humidity:", f"{current['relative_humidity_2m']}%")
    table.add_row(
        "Wind:",
        format_wind(current["wind_speed_10m"], current["wind_direction_10m"], use_fahrenheit),
    )
    table.add_row("Conditions:", f"{icon}  {description}")

    from rich.text import Text
    from rich.align import Align
    from rich.console import Group

    centered_icon = Align.center(Text(icon, justify="center"))

    content = Group(
        Text(""),
        centered_icon,
        Text(""),
        table,
    )

    panel = Panel(
        content,
        title=f"[bold]Current Weather: {title}[/bold]",
        border_style="bright_cyan",
        padding=(1, 2),
    )

    console.print(panel)


def display_forecast(weather, use_fahrenheit, console):
    """Display 5-day forecast in a Rich table wrapped in a panel."""
    daily = weather["daily"]

    table = Table(box=box.ROUNDED, show_lines=False, padding=(0, 1))
    table.add_column("Date", style="bold white", min_width=10)
    table.add_column("Conditions", min_width=22)
    table.add_column("High", justify="right", min_width=8)
    table.add_column("Low", justify="right", min_width=8)
    table.add_column("Precip", justify="right", min_width=8)
    table.add_column("Sunrise", justify="center", min_width=9)
    table.add_column("Sunset", justify="center", min_width=9)

    for i in range(len(daily["time"])):
        date_str = daily["time"][i]
        dt = datetime.fromisoformat(date_str)
        formatted_date = dt.strftime("%a %m/%d")

        code = daily["weather_code"][i]
        icon = get_weather_icon(code)
        desc = get_weather_description(code)
        conditions = f"{icon}  {desc}"

        high = format_temperature(daily["temperature_2m_max"][i], use_fahrenheit)
        low = format_temperature(daily["temperature_2m_min"][i], use_fahrenheit)

        precip = f"{daily['precipitation_sum'][i]:.1f} mm"

        sunrise = format_time(daily["sunrise"][i])
        sunset = format_time(daily["sunset"][i])

        table.add_row(
            formatted_date,
            conditions,
            f"[red]{high}[/red]",
            f"[blue]{low}[/blue]",
            precip,
            sunrise,
            sunset,
        )

    panel = Panel(
        table,
        title="[bold]5-Day Forecast[/bold]",
        border_style="bright_cyan",
        padding=(1, 1),
    )
    console.print(panel)


# --- CLI & Main ---

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Weather CLI — Fetch and display weather from your terminal.",
        epilog="Examples:\n"
               "  python weather.py London\n"
               '  python weather.py "New York" -f\n'
               "  python weather.py Tokyo --fahrenheit\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "city",
        nargs="+",
        help="City name to look up (use quotes for multi-word names)",
    )
    parser.add_argument(
        "-f", "--fahrenheit",
        action="store_true",
        help="Display temperatures in Fahrenheit (default: Celsius)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    city_name = " ".join(args.city)
    use_fahrenheit = args.fahrenheit

    console = Console(force_terminal=True)

    console.print(f"\nFetching weather for [bold cyan]{city_name}[/bold cyan]...\n")

    # Geocode city
    location = geocode_city(city_name)
    if location is None:
        console.print(f"[bold red]City not found:[/bold red] Could not find '{city_name}'. Please check the spelling and try again.")
        sys.exit(1)

    # Fetch weather
    weather = fetch_weather(location["latitude"], location["longitude"], use_fahrenheit)
    if weather is None:
        console.print("[bold red]Error:[/bold red] Could not fetch weather data. Please try again later.")
        sys.exit(1)

    # Display
    display_current_weather(location, weather, use_fahrenheit, console)
    console.print()
    display_forecast(weather, use_fahrenheit, console)
    console.print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    except requests.ConnectionError:
        print("\nError: No internet connection. Please check your network and try again.")
        sys.exit(1)
