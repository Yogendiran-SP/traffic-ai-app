import requests
import geocoder

API_KEY = "f0cfc7c33481b4276cc57af233d0496b"  # Replace with your real API key

def get_current_location():
    g = geocoder.ip('me')  # Uses your IP to approximate location
    if g.ok and g.latlng:
        return g.latlng  # Returns [latitude, longitude]
    else:
        raise Exception("Could not determine location via IP")

def get_weather_data():
    lat, lon = get_current_location()
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = {
            "temperature": data["main"]["temp"],
            "condition": data["weather"][0]["main"],  # e.g., Rain, Clear, Clouds
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }
        return weather
    else:
        raise Exception(f"Failed to fetch weather data: {response.status_code}")
