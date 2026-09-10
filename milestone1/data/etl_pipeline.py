import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

TOTAL_RECORDS = 5000

# 1. Generate Base Geographic & Sector Entities (10 Transit Sectors)
# Centered realistically around an urban metro grid
locations_data = [
    {"LocationKey": 1, "Route_ID": "RT-101", "City": "Metro City", "Zone": "North Zone", "Location": "North Terminal", "Latitude": 13.0827, "Longitude": 80.2707, "Population": 280000, "Population_Density": 16500},
    {"LocationKey": 2, "Route_ID": "RT-102", "City": "Metro City", "Zone": "North Zone", "Location": "North Tech Park", "Latitude": 13.0900, "Longitude": 80.2800, "Population": 210000, "Population_Density": 14200},
    {"LocationKey": 3, "Route_ID": "RT-103", "City": "Metro City", "Zone": "East Zone",  "Location": "East Harbor Bay", "Latitude": 13.0500, "Longitude": 80.2900, "Population": 340000, "Population_Density": 20200},
    {"LocationKey": 4, "Route_ID": "RT-104", "City": "Metro City", "Zone": "East Zone",  "Location": "Coastal Commercial", "Latitude": 13.0400, "Longitude": 80.2850, "Population": 190000, "Population_Density": 11500},
    {"LocationKey": 5, "Route_ID": "RT-105", "City": "Metro City", "Zone": "Central Zone", "Location": "Central Junction", "Latitude": 13.0600, "Longitude": 80.2500, "Population": 320000, "Population_Density": 19800},
    {"LocationKey": 6, "Route_ID": "RT-106", "City": "Metro City", "Zone": "Central Zone", "Location": "Financial Hub", "Latitude": 13.0650, "Longitude": 80.2450, "Population": 260000, "Population_Density": 15400},
    {"LocationKey": 7, "Route_ID": "RT-107", "City": "Metro City", "Zone": "West Zone",  "Location": "West Industrial Park", "Latitude": 13.0700, "Longitude": 80.2000, "Population": 150000, "Population_Density": 8200},
    {"LocationKey": 8, "Route_ID": "RT-108", "City": "Metro City", "Zone": "West Zone",  "Location": "West Residential Belt", "Latitude": 13.0550, "Longitude": 80.1900, "Population": 230000, "Population_Density": 13100},
    {"LocationKey": 9, "Route_ID": "RT-109", "City": "Metro City", "Zone": "South Zone", "Location": "South Suburban Hub", "Latitude": 13.0100, "Longitude": 80.2100, "Population": 310000, "Population_Density": 18400},
    {"LocationKey": 10, "Route_ID": "RT-110", "City": "Metro City", "Zone": "South Zone", "Location": "South Airport Link", "Latitude": 12.9900, "Longitude": 80.1700, "Population": 120000, "Population_Density": 6800},
]
dim_location = pd.DataFrame(locations_data)

# 2. Generate Dim_Weather
weather_data = [
    {"WeatherKey": 1, "Weather": "Clear"},
    {"WeatherKey": 2, "Weather": "Rain"},
    {"WeatherKey": 3, "Weather": "Fog"},
    {"WeatherKey": 4, "Weather": "Snow"}
]
dim_weather = pd.DataFrame(weather_data)

# 3. Generate Dim_Date (Covering March 2024 with Time Hours)
dates = pd.date_range(start="2024-03-01", end="2024-03-20", freq="D")
dim_date = pd.DataFrame({
    "DateKey": range(1, len(dates) + 1),
    "Date": dates.strftime('%Y-%m-%d'),
    "Year": dates.year,
    "Month": dates.strftime('%B'),
    "Day": dates.day,
    "DayOfWeek": dates.strftime('%A')
})

# 4. Generate Fact_Transit with Milestone 2 Geospatial & Reliability Metrics
loc_keys = np.random.choice(dim_location["LocationKey"], size=TOTAL_RECORDS)
date_keys = np.random.choice(dim_date["DateKey"], size=TOTAL_RECORDS)
weather_keys = np.random.choice(dim_weather["WeatherKey"], size=TOTAL_RECORDS, p=[0.45, 0.25, 0.20, 0.10])

# Hourly simulation (06:00 to 23:00)
hours = np.random.choice(range(6, 24), size=TOTAL_RECORDS)

# Base Passenger Count with rush-hour peaks
base_passengers = np.random.randint(80, 450, size=TOTAL_RECORDS)
peak_multiplier = np.where((hours >= 8) & (hours <= 10) | (hours >= 17) & (hours <= 20), 1.6, 1.0)
passengers = (base_passengers * peak_multiplier).astype(int)

# Temperatures based on weather
temperatures = np.round(np.where(
    weather_keys == 1, np.random.normal(24, 3, TOTAL_RECORDS),
    np.where(weather_keys == 2, np.random.normal(16, 2, TOTAL_RECORDS),
    np.where(weather_keys == 3, np.random.normal(11, 2, TOTAL_RECORDS),
    np.random.normal(2, 2, TOTAL_RECORDS)))
), 2)

# Operational Reliability Simulation:
# Rain/Snow increases disruption likelihood
disruption_prob = np.where(weather_keys == 2, 0.25, np.where(weather_keys == 4, 0.40, 0.08))
is_disrupted = np.random.binomial(1, disruption_prob)
delays = np.where(is_disrupted == 1, np.random.randint(15, 65, TOTAL_RECORDS), np.random.randint(0, 5, TOTAL_RECORDS))
trip_status = np.where(is_disrupted == 1, "Delayed", "On-Time")

fact_transit = pd.DataFrame({
    "Trip_ID": [f"TRIP-{10000 + i}" for i in range(TOTAL_RECORDS)],
    "DateKey": date_keys,
    "LocationKey": loc_keys,
    "WeatherKey": weather_keys,
    "Time_Hour": [f"{h:02d}:00" for h in hours],
    "Passenger_Count": passengers,
    "Temperature": temperatures,
    "Delay_Minutes": delays,
    "Is_Disrupted": is_disrupted,
    "Trip_Status": trip_status
})

# Export Normalized Relational Tables
dim_location.to_csv("Dim_Location.csv", index=False)
dim_date.to_csv("Dim_Date.csv", index=False)
dim_weather.to_csv("Dim_Weather.csv", index=False)
fact_transit.to_csv("Fact_Transit.csv", index=False)

print("ETL execution successful!")
print(f"Total Trips Generated: {len(fact_transit)}")
print(f"Total Disrupted Trips: {fact_transit['Is_Disrupted'].sum()}")
print("Generated Files: Dim_Location.csv, Dim_Date.csv, Dim_Weather.csv, Fact_Transit.csv")