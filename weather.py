import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
import json

# Setup the coordinates of the buildings
locations = {
    "Aule_I": {
        "latitude": 45.065037,
        "longitude": 7.658205,
    }
}

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Base URL for the API
url = "https://api.open-meteo.com/v1/forecast"

# Liste pour stocker toutes les données
all_weather_data = []

# Processing the locations and querying the API
for building_name, building_data in locations.items():
    query_params = {
        "latitude": building_data["latitude"],
        "longitude": building_data["longitude"],
        "current": ["temperature_2m", "precipitation", "wind_speed_10m", "wind_direction_10m"],
        "hourly": ["temperature_2m", "precipitation_probability", "wind_speed_10m", "wind_direction_10m"],
        "forecast_days": 1
    }

    responses = openmeteo.weather_api(url, params=query_params)
    for response in responses:
        # Préparer les données pour le bâtiment
        weather_data = {
            "building_name": building_name,
            "coordinates": {
                "latitude": float(response.Latitude()),
                "longitude": float(response.Longitude())
            },
            "elevation": float(response.Elevation()),
            "timezone": {
                "name": response.Timezone(),
                "abbreviation": response.TimezoneAbbreviation(),
                "utc_offset_seconds": response.UtcOffsetSeconds()
            },
            "current_weather": {},
            "hourly_weather": []
        }

        # Données actuelles
        current = response.Current()
        weather_data["current_weather"] = {
            "time": current.Time(),
            "temperature_2m": float(current.Variables(0).Value()),
            "precipitation": float(current.Variables(1).Value()),
            "wind_speed_10m": float(current.Variables(2).Value()),
            "wind_direction_10m": float(current.Variables(3).Value())
        }

        # Données horaires
        hourly = response.Hourly()
        hourly_dates = pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )
        hourly_data = {
            "temperature_2m": [float(val) for val in hourly.Variables(0).ValuesAsNumpy()],
            "precipitation_probability": [float(val) for val in hourly.Variables(1).ValuesAsNumpy()],
            "wind_speed_10m": [float(val) for val in hourly.Variables(2).ValuesAsNumpy()],
            "wind_direction_10m": [float(val) for val in hourly.Variables(3).ValuesAsNumpy()]
        }

        # Ajout des données horaires dans le format JSON
        for i, date in enumerate(hourly_dates):
            weather_data["hourly_weather"].append({
                "time": str(date),
                "temperature_2m": hourly_data["temperature_2m"][i],
                "precipitation_probability": hourly_data["precipitation_probability"][i],
                "wind_speed_10m": hourly_data["wind_speed_10m"][i],
                "wind_direction_10m": hourly_data["wind_direction_10m"][i]
            })

        # Ajout au JSON global
        all_weather_data.append(weather_data)

# Sauvegarde dans un fichier JSON
with open("weather_data.json", "w") as json_file:
    json.dump(all_weather_data, json_file, indent=4)

print("Weather data has been saved to weather_data.json")


# Function to send the JSON to the adaptor
#def send_to_adaptor(json_file_path, adaptor_url):
#    try:
#        with open(json_file_path, "r") as file:
#            data = json.load(file)
#
#        # Send to the adaptor
#        response = requests.post(adaptor_url, json=data, headers={"Content-Type": "application/json"})
#
#        if response.status_code == 200:
#            print("Data successfully sent to adaptor.")
#        else:
#            print(f"Failed to send data to adaptor. Status code: {response.status_code}, Response: {response.text}")
#
#    except Exception as e:
#        print(f"Error while sending data to adaptor: {e}")
#
#ADAPTOR_URL = "http://localhost:5001/receive-json"  # Will have to put here the real adaptor URL
#send_to_adaptor("weather_data.json", ADAPTOR_URL)