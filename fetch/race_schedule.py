import requests
import json
import time

def get_race_schedule(year):
    """Get race schedule and circuit information for a specific year"""
    url = f"https://ergast.com/api/f1/{year}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        schedule = data["MRData"]["RaceTable"].get("Races", [])
        return schedule
    return []

def save_race_schedules(years=[2022, 2023, 2024]):
    schedules = {}
    for year in years:
        print(f"Fetching {year} race schedule...")
        schedules[year] = get_race_schedule(year)
        time.sleep(1)  # Be nice to the API

    with open("data/race_schedules.json", "w") as f:
        json.dump(schedules, f, indent=4)
    
    print("Race schedules saved to data/race_schedules.json")
