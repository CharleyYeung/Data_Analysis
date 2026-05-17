import requests
import json
import sqlite3
from datetime import datetime, timezone

def run_etl():
    cities = {
        "Tokyo": {"lat": 35.6895, "lon": 139.6917},
        "London": {"lat": 51.5074, "lon": -0.1278},
        "Hong Kong": {"lat": 22.3193, "lon": 114.1694},
        "New York": {"lat": 40.7128, "lon": -74.0060},
        "Vancouver": {"lat": 49.2827, "lon": -123.1207},
        "Sydney": {"lat": -33.8688, "lon": 151.2093},
        "Bangkok": {"lat": 13.7563, "lon": 100.5018}
    }
    
    raw_results = []
    current_utc_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    for city, coord in cities.items():
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coord['lat']}&longitude={coord['lon']}&current_weather=true"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            current_weather = data['current_weather']
            raw_results.append((city, current_weather['temperature'], current_weather['time']))
        except Exception as e:
            print(f"Failed to fetch data for {city}: {e}")

    with sqlite3.connect(':memory:') as conn:
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE weather_staging (city TEXT, temp REAL, raw_time TEXT)')
        cursor.executemany('INSERT INTO weather_staging VALUES (?, ?, ?)', raw_results)
        
        query = """
        SELECT 
            city, temp, 
            REPLACE(raw_time, 'T', ' ') as full_timestamp,
            SUBSTR(raw_time, 1, 10) as date_string
        FROM weather_staging
        """
        cursor.execute(query)
        transformed_rows = cursor.fetchall()

    final_json = []

    for row in transformed_rows:
        city, temp, full_timestamp, date_string = row
        
        if temp < 15:
            cat_status = "Cloudy is snuggling in the blankets on the bed."
        elif 15 <= temp <= 25:
            cat_status = "Cloudy feels comfy!"
        else:
            cat_status = "Cloudy is sticking his tongue out to cool down."

        final_json.append({
            "city": city,
            "temperature": f"{temp}°C",
            "date": date_string,
            "timestamp": full_timestamp,
            "status": cat_status,
            "last_updated_utc": current_utc_time
        })

    output_path = 'src/data/weather_data.json'
    with open(output_path, 'w') as f:
        json.dump(final_json, f, indent=4)
    
    print(f"ETL Job Completed successfully! Output saved to: {output_path}")

if __name__ == "__main__":
    run_etl()