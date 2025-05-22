import requests
import json
import time
from datetime import datetime

def get_race_schedule(year):
    """Get race schedule and metadata for a specific year"""
    url = f"https://ergast.com/api/f1/{year}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["MRData"]["RaceTable"].get("Races", [])
    return []

def get_race_results(year, round_num):
    """Get detailed race results for a specific race"""
    url = f"https://ergast.com/api/f1/{year}/{round_num}/results.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        races = data["MRData"]["RaceTable"].get("Races", [])
        if races and len(races) > 0:
            return races[0].get("Results", [])
    return []

def get_qualifying_results(year, round_num):
    """Get qualifying results for a specific race"""
    url = f"https://ergast.com/api/f1/{year}/{round_num}/qualifying.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        races = data["MRData"]["RaceTable"].get("Races", [])
        if races and len(races) > 0:
            return races[0].get("QualifyingResults", [])
    return []

def get_driver_standings(year):
    """Get driver standings for the entire season"""
    url = f"https://ergast.com/api/f1/{year}/driverStandings.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        standings_lists = data["MRData"]["StandingsTable"].get("StandingsLists", [])
        if standings_lists and len(standings_lists) > 0:
            return standings_lists[-1].get("DriverStandings", [])  # Get latest standings
    return []

def get_constructor_standings(year):
    """Get constructor standings for the entire season"""
    url = f"https://ergast.com/api/f1/{year}/constructorStandings.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        standings_lists = data["MRData"]["StandingsTable"].get("StandingsLists", [])
        if standings_lists and len(standings_lists) > 0:
            return standings_lists[-1].get("ConstructorStandings", [])  # Get latest standings
    return []

# Initialize main data structure
f1_data = {}

# Process years 2022-2024
for year in range(2022, 2025):
    print(f"\nProcessing year {year}...")
    
    # Initialize year data
    f1_data[year] = {
        "races": {},
        "driver_standings": {},
        "constructor_standings": {}
    }
    
    # Get race schedule for the year
    races = get_race_schedule(year)
    
    # Process each race
    for race in races:
        try:
            round_num = race["round"]
            race_name = race["raceName"]
            print(f"Processing {race_name}...")
            
            # Build race data structure
            race_data = {
                "name": race_name,
                "round": round_num,
                "date": race["date"],
                "time": race.get("time", ""),
                "circuit": {
                    "name": race["Circuit"]["circuitName"],
                    "location": race["Circuit"]["Location"]["locality"],
                    "country": race["Circuit"]["Location"]["country"],
                    "lat": race["Circuit"]["Location"]["lat"],
                    "long": race["Circuit"]["Location"]["long"]
                },
                "qualifying": get_qualifying_results(year, round_num),
                "results": get_race_results(year, round_num)
            }
            
            # Add race data to year
            f1_data[year]["races"][round_num] = race_data
            
            time.sleep(1)  # Be nice to the API
            
        except Exception as e:
            print(f"Error processing race {race_name}: {str(e)}")
            continue
    
    # Get season standings
    try:
        print(f"Getting season standings for {year}...")
        f1_data[year]["driver_standings"] = get_driver_standings(year)
        f1_data[year]["constructor_standings"] = get_constructor_standings(year)
    except Exception as e:
        print(f"Error getting standings for {year}: {str(e)}")

# Save complete dataset
output_file = "f1_complete_data_2022_2024.json"
with open(output_file, "w") as f:
    json.dump(f1_data, f, indent=4)

print(f"\nComplete F1 data has been saved to {output_file}")

# Create a summary with key statistics
summary = {}
for year in f1_data:
    races_data = f1_data[year]["races"]
    driver_standings = f1_data[year]["driver_standings"]
    constructor_standings = f1_data[year]["constructor_standings"]
    
    summary[year] = {
        "total_races": len(races_data),
        "champion": next((
            {
                "name": f"{driver['Driver']['givenName']} {driver['Driver']['familyName']}",
                "points": driver['points'],
                "wins": driver['wins']
            }
            for driver in driver_standings 
            if driver["position"] == "1"
        ), {"name": "TBD", "points": "0", "wins": "0"}),
        "constructor_champion": next((
            {
                "name": constructor["Constructor"]["name"],
                "points": constructor["points"],
                "wins": constructor["wins"]
            }
            for constructor in constructor_standings 
            if constructor["position"] == "1"
        ), {"name": "TBD", "points": "0", "wins": "0"}),
        "races_by_country": {},
        "pole_positions": {},
        "race_wins": {}
    }
    
    # Count races by country and collect pole/win statistics
    for round_data in races_data.values():
        country = round_data["circuit"]["country"]
        summary[year]["races_by_country"][country] = summary[year]["races_by_country"].get(country, 0) + 1
        
        # Count pole positions
        if round_data["qualifying"] and len(round_data["qualifying"]) > 0:
            pole_driver = f"{round_data['qualifying'][0]['Driver']['givenName']} {round_data['qualifying'][0]['Driver']['familyName']}"
            summary[year]["pole_positions"][pole_driver] = summary[year]["pole_positions"].get(pole_driver, 0) + 1
        
        # Count race wins
        if round_data["results"] and len(round_data["results"]) > 0:
            winner = f"{round_data['results'][0]['Driver']['givenName']} {round_data['results'][0]['Driver']['familyName']}"
            summary[year]["race_wins"][winner] = summary[year]["race_wins"].get(winner, 0) + 1

# Save summary
summary_file = "f1_summary_2022_2024.json"
with open(summary_file, "w") as f:
    json.dump(summary, f, indent=4)

print(f"Summary statistics have been saved to {summary_file}")