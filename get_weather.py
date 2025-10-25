
import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta
import re

def safe_int_convert(value):
    """Safely converts a string to an integer, returning None if conversion fails."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def get_weather_forecast():
    location_id = "3067696"  # Hardcoded for Prague
    weather_url = f"https://weather-broker-cdn.api.bbci.co.uk/en/forecast/rss/3day/{location_id}"

    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)

        weather_forecast = {}

        # Regex to parse the title for day name and description
        title_regex = re.compile(r"([^:]+): (.*), Minimum Temperature")

        for i, item in enumerate(root.findall(".//item")):
            title = item.find("title").text
            description = item.find("description").text

            # Date calculation
            today = datetime.now()
            if "Today" in title:
                local_date = today.strftime("%Y-%m-%d")
            else:
                local_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")

            # Extracting weather description from title
            match = title_regex.match(title)
            if match:
                enhanced_weather_desc = match.group(2).strip()
            else:
                enhanced_weather_desc = "N/A"

            # Parsing the description field for detailed forecast
            details = {"enhancedWeatherDescription": enhanced_weather_desc}
            parts = description.split(', ')
            for part in parts:
                if ': ' in part:
                    key, value = part.split(': ', 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "Maximum Temperature":
                        temps = re.match(r"(\d+)°C \((\d+)°F\)", value)
                        if temps:
                            details["maxTemperatureC"] = safe_int_convert(temps.group(1))
                            details["maxTemperatureF"] = safe_int_convert(temps.group(2))
                    elif key == "Minimum Temperature":
                        temps = re.match(r"(\d+)°C \((\d+)°F\)", value)
                        if temps:
                            details["minTemperatureC"] = safe_int_convert(temps.group(1))
                            details["minTemperatureF"] = safe_int_convert(temps.group(2))
                    elif key == "Wind Direction":
                        details["windDirection"] = value
                    elif key == "Wind Speed":
                        details["windSpeedMph"] = safe_int_convert(value.replace("mph", ""))
                    elif key == "Visibility":
                        details["visibility"] = value
                    elif key == "Pressure":
                        details["pressureMb"] = safe_int_convert(value.replace("mb", ""))
                    elif key == "Humidity":
                        details["humidity"] = safe_int_convert(value.replace("%", ""))
                    elif key == "UV Risk":
                        details["uvRisk"] = safe_int_convert(value)
                    elif key == "Pollution":
                        details["pollution"] = value if value != "--" else None
                    elif key == "Sunrise":
                        details["sunrise"] = value
                    elif key == "Sunset":
                        details["sunset"] = value

            weather_forecast[local_date] = details

        return json.dumps(weather_forecast, indent=2)

    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {e}"
    except (ET.ParseError, AttributeError):
        return "Error: Unable to parse XML response."

if __name__ == "__main__":
    forecast_json = get_weather_forecast()
    print(forecast_json)
