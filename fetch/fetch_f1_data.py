import requests
import json
import csv
import time
from datetime import datetime

def get_all_rounds_data(year, data_type):
    """Fetch all rounds data for a specific year and data type (qualifying or results)"""
    # First get the race schedule to know how many rounds
    schedule_url = f"https://ergast.com/api/f1/{year}.json"
    response = requests.get(schedule_url)
    if response.status_code != 200:
        return []

    races = response.json()["MRData"]["RaceTable"]["Races"]
    all_data = []

    for race in races:
        round_num = race["round"]
        print(f"Fetching {data_type} for round {round_num}...")
        
        # Fetch data for this round
        url = f"https://ergast.com/api/f1/{year}/{round_num}/{data_type}.json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "RaceTable" in data["MRData"] and "Races" in data["MRData"]["RaceTable"]:
                races = data["MRData"]["RaceTable"]["Races"]
                if races:
                    all_data.extend(races)
        time.sleep(1)  # Be nice to the API

    return all_data

def save_qualifying_data(year, data):
    """Save qualifying data to CSV and JSON"""
    # Save JSON
    json_file = f"qualifying_{year}_all_rounds.json"
    with open(json_file, 'w') as f:
        json.dump({"MRData": {"RaceTable": {"Races": data}}}, f, indent=4)

    # Save CSV
    csv_file = f"qualifying_{year}_all_rounds.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["year", "round", "raceName", "date", "driverName", "constructorName", "position", "Q1", "Q2", "Q3"])
        writer.writeheader()
        for race in data:
            for quali in race.get("QualifyingResults", []):
                writer.writerow({
                    "year": race.get("season"),
                    "round": race.get("round"),
                    "raceName": race.get("raceName"),
                    "date": race.get("date"),
                    "driverName": f"{quali['Driver']['givenName']} {quali['Driver']['familyName']}",
                    "constructorName": quali["Constructor"]["name"],
                    "position": quali.get("position"),
                    "Q1": quali.get("Q1", ""),
                    "Q2": quali.get("Q2", ""),
                    "Q3": quali.get("Q3", "")
                })

def save_results_data(year, data):
    """Save race results data to CSV and JSON"""
    # Save JSON
    json_file = f"results_{year}_all_rounds.json"
    with open(json_file, 'w') as f:
        json.dump({"MRData": {"RaceTable": {"Races": data}}}, f, indent=4)

    # Save CSV
    csv_file = f"results_{year}_all_rounds.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["year", "round", "raceName", "date", "driverName", "constructorName", 
                                             "position", "points", "status", "grid", "laps", "fastestLapTime"])
        writer.writeheader()
        for race in data:
            for result in race.get("Results", []):
                writer.writerow({
                    "year": race.get("season"),
                    "round": race.get("round"),
                    "raceName": race.get("raceName"),
                    "date": race.get("date"),
                    "driverName": f"{result['Driver']['givenName']} {result['Driver']['familyName']}",
                    "constructorName": result["Constructor"]["name"],
                    "position": result.get("position"),
                    "points": result.get("points"),
                    "status": result.get("status"),
                    "grid": result.get("grid"),
                    "laps": result.get("laps"),
                    "fastestLapTime": result.get("FastestLap", {}).get("Time", {}).get("time", "")
                })

def save_schedule(year):
    """Save race schedule to CSV and JSON"""
    url = f"https://ergast.com/api/f1/{year}.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        # Save JSON
        with open(f"schedule_{year}.json", 'w') as f:
            json.dump(data, f, indent=4)
        
        # Save CSV
        races = data["MRData"]["RaceTable"]["Races"]
        with open(f"schedule_{year}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["year", "round", "raceName", "date", "time", 
                                                 "circuitName", "locality", "country", "lat", "long"])
            writer.writeheader()
            for race in races:
                writer.writerow({
                    "year": race.get("season"),
                    "round": race.get("round"),
                    "raceName": race.get("raceName"),
                    "date": race.get("date"),
                    "time": race.get("time", ""),
                    "circuitName": race["Circuit"]["circuitName"],
                    "locality": race["Circuit"]["Location"]["locality"],
                    "country": race["Circuit"]["Location"]["country"],
                    "lat": race["Circuit"]["Location"]["lat"],
                    "long": race["Circuit"]["Location"]["long"]
                })

def save_standings(year):
    """Save driver and constructor standings to CSV and JSON"""
    # Driver Standings
    url = f"https://ergast.com/api/f1/{year}/driverStandings.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        # Save JSON
        with open(f"driver_standings_{year}.json", 'w') as f:
            json.dump(data, f, indent=4)
        
        # Save CSV
        standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]
        with open(f"driver_standings_{year}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["year", "position", "driverName", "constructorName", "points", "wins"])
            writer.writeheader()
            for standing in standings:
                writer.writerow({
                    "year": year,
                    "position": standing["position"],
                    "driverName": f"{standing['Driver']['givenName']} {standing['Driver']['familyName']}",
                    "constructorName": standing["Constructors"][0]["name"],
                    "points": standing["points"],
                    "wins": standing["wins"]
                })
    
    time.sleep(1)
    
    # Constructor Standings
    url = f"https://ergast.com/api/f1/{year}/constructorStandings.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        
        # Save JSON
        with open(f"constructor_standings_{year}.json", 'w') as f:
            json.dump(data, f, indent=4)
        
        # Save CSV
        standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]["ConstructorStandings"]
        with open(f"constructor_standings_{year}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["year", "position", "constructorName", "points", "wins"])
            writer.writeheader()
            for standing in standings:
                writer.writerow({
                    "year": year,
                    "position": standing["position"],
                    "constructorName": standing["Constructor"]["name"],
                    "points": standing["points"],
                    "wins": standing["wins"]
                })

# Process years 2022-2024
for year in range(2022, 2025):
    print(f"\nProcessing year {year}...")
    
    # 1. Race Schedule
    print("Fetching race schedule...")
    save_schedule(year)
    time.sleep(1)
    
    # 2. All Race Results for the year
    print(f"Fetching all race results for {year}...")
    results_data = get_all_rounds_data(year, "results")
    save_results_data(year, results_data)
    time.sleep(1)
    
    # 3. All Qualifying Results for the year
    print(f"Fetching all qualifying results for {year}...")
    qualifying_data = get_all_rounds_data(year, "qualifying")
    save_qualifying_data(year, qualifying_data)
    time.sleep(1)
    
    # 4. Standings
    print(f"Fetching standings for {year}...")
    save_standings(year)
    time.sleep(1)

print("\nAll data has been downloaded in both JSON and CSV formats!")
print("\nFiles created for each year (2022-2024):")
print("1. schedule_[year].csv/json - Race schedule and circuit information")
print("2. results_[year]_all_rounds.csv/json - All race results for the year")
print("3. qualifying_[year]_all_rounds.csv/json - All qualifying results for the year")
print("4. driver_standings_[year].csv/json - Final driver standings")
print("5. constructor_standings_[year].csv/json - Final constructor standings")
