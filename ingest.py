# Fetches LoL esports data from Leaguepedia's Cargo API
# Login flow based on MediaWiki's API:Login docs, explained with help from Claude (AI)

import requests
from dotenv import load_dotenv
import os
import json
import time
import sqlite3

# Load bot credentials from .env
load_dotenv()
user = os.getenv("LEAGUEPEDIA_USER")
password = os.getenv("LEAGUEPEDIA_PASSWORD")
url = "https://lol.fandom.com/api.php"

# Check credentials loaded
print(f"User: {user}")
print(f"Password: {password is not None}")

# Session keeps cookies, so we stay logged in between requests
session = requests.Session()

# Step 1: ask the API for a login token
token_params = {
    "action": "query",
    "meta": "tokens",
    "type": "login",
    "format": "json",
}

response = session.get(url, params=token_params)
data = response.json()

login_token = data["query"]["tokens"]["logintoken"]

# Step 2: log in with bot password and token
login_params = {
    "action": "login",
    "lgname": user,
    "lgpassword": password,
    "lgtoken": login_token,
    "format": "json",
}

response = session.post(url, data=login_params)
data = response.json()

params = {
    "action": "cargoquery",
    "format": "json",
    "tables": "ScoreboardGames",
    "fields": "GameId, OverviewPage, Gamelength_Number",
    "where": 'OverviewPage = "2025 Season World Championship/Main Event"',
    "order_by": "GameId",
}

# Pagination: fetch rows page by page
list_of_games = []
limit = 20
offset = 0

while True:
    # Send query with the logged-in session
    params["limit"] = limit
    params["offset"] = offset
    response = session.get(url, params=params)
    data = response.json()
    list_of_games.extend(data["cargoquery"])
    if len(data["cargoquery"]) < limit: # A page shorter than limit means there's nothing left
        break
    offset += limit
    # Pause between requests to stay under the rate limit  from Leaguepedia's API
    time.sleep(1)

# Unique games should match the total
gamed_ids = set()
for game in list_of_games:
    gamed_ids.add(game["title"]["GameId"])
print(len(gamed_ids))

# Save raw data to a JSON file
os.makedirs("data", exist_ok=True)
with open("data/raw_games.json", "w", encoding="utf-8") as file:
    json.dump(list_of_games, file, ensure_ascii=False, indent=4)

# Load the raw data back from the JSON file to verify it was saved correctly
with open("data/raw_games.json", "r", encoding="utf-8") as file:
    loaded_data = json.load(file)
    print(f"Loaded {len(loaded_data)} games from JSON file.")

# Create the SQLite database and tables
con = sqlite3.connect("data/fantasy.db")
cur = con.cursor()

# Create the table if it doesn't exist
# Games table
cur.execute("""
 CREATE TABLE IF NOT EXISTS games (
    game_id TEXT PRIMARY KEY,
    overview_page TEXT,
    gamelength_number REAL,
    date_time_utc TEXT
    )
""")

# Players table
cur.execute("""
 CREATE TABLE IF NOT EXISTS players (
    link TEXT PRIMARY KEY,
    role_number INTEGER,
    team TEXT,
    price REAL
    )
""")

# Perfomances table
cur.execute("""
 CREATE TABLE IF NOT EXISTS performances (
    game_id TEXT,
    link TEXT,
    kills INTEGER,
    deaths INTEGER,
    assists INTEGER,
    cs INTEGER,
    gold INTEGER,
    damage_to_champions INTEGER,
    vision_score INTEGER,
    player_win TEXT,
    team_kills INTEGER,
    PRIMARY KEY (game_id, link)
    )
""")

# Save changes to the database
con.commit()
con.close()
