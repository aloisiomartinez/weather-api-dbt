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

def connect_to_database():
  logger.info("Connecting to the PostgreSQL Database ...")
  try:
    conn = psycopg2.connect(
      dbname = os.getenv('POSTGRES_DB'),
      user = os.getenv('POSTGRES_USER'),
      password = os.getenv('POSTGRES_PASSWORD'),
      host = os.getenv('POSTGRES_HOST'),
      port = os.getenv('POSTGRES_PORT')
    )
    logger.info("Successfully connect to Database")
    return conn
  except psycopg2.Error as e:
    logger.error(f"Database connection failed: {e}")
    return None
  
def create_schema_and_table(conn: psycopg2.connect):
  if conn is None:
    logger.error("No database connection available")
    return None

  try:
    with conn.cursor() as cursor:
      cursor.execute("CREATE SCHEMA IF NOT EXISTS weather_data;")
      cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS weather_data.city_weather (
            id SERIAL PRIMARY KEY,
            city TEXT,
            temperature FLOAT,
            weather_description TEXT,
            wind_speed FLOAT,
            time TIMESTAMP,
            insert_at TIMESTAMP DEFAULT NOW(),
            timezone INTEGER
        );
      """)
      conn.commit()
      logger.info("Schema and table created successfully")
  except psycopg2.Error as e:
    logger.error(f"Error creating schema and table: {e}")
    return None

def insert_weather_data(conn, city, weather_data):
  if conn is None:
    logger.error("No Database connection available.")
    return None

  try:
    with conn.cursor() as cursor:
        cursor.execute("""  
          INSERT INTO weather_data.city_weather(
            city,
            temperature,
            weather_description,
            wind_speed,
            time,
            insert_at,
            timezone
          ) VALUES(%s, %s, %s, %s, to_timestamp(%s), NOW(), %s);
        """, (
          weather_data['name'],
          weather_data['main']['temp'],
          weather_data['weather'][0]['description'],
          weather_data['wind']['speed'],
          weather_data['dt'],
          weather_data['timezone']
        ))
        conn.commit()
        logger.info(f"Weather data for {city} inserted successfully.")
  except psycopg2.Error as e:
    logger.error(f"Error inserting weather data: {e}")


if __name__ == "__main__":
   city = "Bagé"
   weather_data = get_weather_data(city)
   conn = connect_to_database()
   create_schema_and_table(conn)
   insert_weather_data(conn, city, weather_data)
   conn.close()