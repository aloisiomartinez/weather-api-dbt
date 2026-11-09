import requests
import os
import logging
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_weather_data(city: str):
  api_key = os.getenv('OPENWEATHER_API_KEY')

  if not api_key:
    logger.error("Api Key not found!")
    return None

  base_url = "https://api.openweathermap.org/data/2.5/weather"
  params = {
    'q': city,
    'appid': api_key,
    'units': 'metric'
  }

  try:
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    weather_data = response.json()
    logger.info(f"Weather data for {city}: {weather_data}")
    return weather_data
  except requests.RequestException as e:
    logger.error(f"Error fetching weather data: {e}")
    return None

if __name__ == "__main__":
  city = "Bagé"
  get_weather_data(city)

