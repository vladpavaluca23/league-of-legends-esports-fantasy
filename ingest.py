# Fetches LoL esports data from Leaguepedia's Cargo API
# Login flow based on MediaWiki's API:Login docs, explained with help from Claude (AI)

import requests
from dotenv import load_dotenv
import os
import json
import time
import sqlite3
import sys

# Constants
N_GAMES = 20 #Number of games to fetch for calculating prices

def fetch_data(params):
    # Pagination: fetch rows page by page
    rows = []
    limit = 500
    offset = 0
    while True:
        # Send query with the logged-in session
        params["limit"] = limit
        params["offset"] = offset
        response = session.get(url, params=params)
        data = response.json()
        rows.extend(data["cargoquery"])
        if len(data["cargoquery"]) < limit: # A page shorter than limit means there's nothing left
            break
        offset += limit
        # Pause between requests to stay under the rate limit  from Leaguepedia's API
        time.sleep(1)
    return rows

def fetch_history(link, cutoff_date):
    # Fetches the last N_GAMES games for a player before the cutoff date
    history_params = {
        "action": "cargoquery",
        "format": "json",
        "tables": "ScoreboardPlayers=SP, ScoreboardGames=SG",
        "join_on": "SP.GameId = SG.GameId",
        "fields": "SP.GameId, SP.Link, SP.Team, SP.Role_Number, SP.DateTime_UTC, SP.OverviewPage, "
        "SP.Kills, SP.Deaths, SP.Assists, SP.CS, SP.Gold, SP.DamageToChampions, "
        "SP.VisionScore, SP.PlayerWin, SP.TeamKills, SG.Gamelength_Number",
        "where": f'SP.Link = "{link}" AND SP.DateTime_UTC < "{cutoff_date}"',
        "order_by": "SP.DateTime_UTC DESC",
        "limit": N_GAMES,
    }
    response = session.get(url, params=history_params)
    data = response.json()
    return data["cargoquery"]

# Load bot credentials from .env
load_dotenv()
user = os.getenv("LEAGUEPEDIA_USER")
password = os.getenv("LEAGUEPEDIA_PASSWORD")
url = "https://lol.fandom.com/api.php"

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

# Parameters for games table
params = {
    "action": "cargoquery",
    "format": "json",
    "tables": "ScoreboardGames",
    "fields": "GameId, OverviewPage, Gamelength_Number, DateTime_UTC",
    "where": 'OverviewPage = "2025 Season World Championship/Main Event"',
    "order_by": "GameId",
}

list_of_games = fetch_data(params)

#Unique games should match the total
game_ids = set()
for game in list_of_games:
    game_ids.add(game["title"]["GameId"])

# Save raw data to a JSON file
os.makedirs("data", exist_ok=True)
with open("data/raw_games.json", "w", encoding="utf-8") as file:
    json.dump(list_of_games, file, ensure_ascii=False, indent=4)

# Load the raw data back from the JSON file to verify it was saved correctly
with open("data/raw_games.json", "r", encoding="utf-8") as file:
    loaded_data = json.load(file)


# Parameters for performances table
performance_params = {
    "action": "cargoquery",
    "format": "json",
    "tables": "ScoreboardPlayers",
    "fields": "GameId, Link, Role_Number, Team, Kills, Deaths, Assists, CS, Gold, DamageToChampions, VisionScore, PlayerWin, TeamKills",
    "where": 'OverviewPage = "2025 Season World Championship/Main Event"',
    "order_by": "GameId, Link",
}

list_of_performances = fetch_data(performance_params)

# Save raw data to a JSON file
with open("data/raw_performance.json", "w", encoding="utf-8") as file:
    json.dump(list_of_performances, file, ensure_ascii=False, indent=4)

# Create the SQLite database and tables
con = sqlite3.connect("data/fantasy.db")
cur = con.cursor()

# DATABASE TABLES CREAT

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

# Performances table
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

# History table (last N games played)
cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        game_id TEXT,
        link TEXT,
        team TEXT,
        role_number INTEGER,
        date_time_utc TEXT,
        overview_page TEXT,
        kills INTEGER,
        deaths INTEGER,
        assists INTEGER,
        cs INTEGER,
        gold INTEGER,
        damage_to_champions INTEGER,
        vision_score INTEGER,
        player_win TEXT,
        team_kills INTEGER,
        gamelength_number REAL,
        PRIMARY KEY (game_id, link)
    )
""")

# Load games data in Table: games
for row in loaded_data:
    item = row["title"]
    cur.execute(
        """
        INSERT INTO games (game_id, overview_page, gamelength_number, date_time_utc) VALUES(?, ?, ?, ?)
        ON CONFLICT (game_id) DO UPDATE SET
            overview_page = excluded.overview_page,
            gamelength_number = excluded.gamelength_number,
            date_time_utc = excluded.date_time_utc
        """,
        (item["GameId"], item["OverviewPage"], float(item["Gamelength Number"]), item["DateTime UTC"])
    )

# Load the raw data back from the JSON
with open("data/raw_performance.json", "r", encoding="utf-8") as file:
    loaded_performances = json.load(file)

# Prepare performance rows for insertion
performance_rows = []
# Build one tuple per performance for executemany
for row in loaded_performances:
    item = row["title"]
    performance_rows.append((
        item["GameId"],
        item["Link"],
        int(item["Kills"]),
        int(item["Deaths"]),
        int(item["Assists"]),
        int(item["CS"]),
        int(item["Gold"]),
        int(item["DamageToChampions"]),
        int(item["VisionScore"]),
        item["PlayerWin"],
        int(item["TeamKills"])
    ))

# Load performance data in Table: performances
cur.executemany(
    """
        INSERT INTO performances (game_id, link, kills, deaths, assists, cs, gold, damage_to_champions, vision_score, player_win, team_kills) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (game_id, link) DO UPDATE SET
            kills = excluded.kills,
            deaths = excluded.deaths,
            assists = excluded.assists,
            cs = excluded.cs,
            gold = excluded.gold,
            damage_to_champions = excluded.damage_to_champions,
            vision_score = excluded.vision_score,
            player_win = excluded.player_win,
            team_kills = excluded.team_kills
    """,
    performance_rows
)

# Create a set of unique player links from the performances data
links = set()
for row in loaded_performances:
    item = row["title"]
    links.add(item["Link"])

# Create a set of unique triplets (link, role_number, team) from the performances data
triplets = set()
for row in loaded_performances:
    item = row["title"]
    triplet = (item["Link"], int(item["Role Number"]), item["Team"])
    triplets.add(triplet)

# Stop if a player has more than one role or team (likely corrupted data).
# Used Claude (AI) for guidance.
if len(links) != len(triplets):
    sys.exit("Error: The number of unique links does not match the number of unique triplets (link, role_number, team).")

# Load player data in Table: players
cur.executemany(
    """
        INSERT INTO players (link, role_number, team) VALUES (?, ?, ?)
        ON CONFLICT (link) DO UPDATE SET
            role_number = excluded.role_number,
            team = excluded.team
    """,
    triplets
)

# Fetch the last N_GAMES of every player before the Main Event
cutoff_date = cur.execute("SELECT MIN(date_time_utc) FROM games").fetchone()[0]
history = []
for link in links:
    rows = fetch_history(link, cutoff_date)
    history.extend(rows)
    time.sleep(1)

# Save raw data to a JSON file
with open("data/raw_history.json", "w", encoding="utf-8") as file:
    json.dump(history, file, ensure_ascii=False, indent=4)

# Load the raw data back from the JSON
with open("data/raw_history.json", "r", encoding="utf-8") as file:
    loaded_history = json.load(file)

# Leaguepedia matches links case-insensitively
# Map each lowercase link to its spelling in players, so both tables use the same link.
correct_link = {}
for link in links:
    correct_link[link.lower()] = link

#Prepare data for history insertion in DB
history_rows = []
# Build one tuple per performance for executemany
for row in loaded_history:
    item = row["title"]
    history_rows.append((
        item["GameId"],
        correct_link[item["Link"].lower()],
        item["Team"],
        int(item["Role Number"]),
        item["DateTime UTC"],
        item["OverviewPage"],
        int(item["Kills"]),
        int(item["Deaths"]),
        int(item["Assists"]),
        int(item["CS"]),
        int(item["Gold"]),
        int(item["DamageToChampions"]),
        int(item["VisionScore"]),
        item["PlayerWin"],
        int(item["TeamKills"]),
        float(item["Gamelength Number"])
    ))

# Load performance data in Table: history
cur.executemany(
    """
        INSERT INTO history (game_id, link, team, role_number, date_time_utc, overview_page, kills, deaths, assists, cs, gold, damage_to_champions, vision_score, player_win, team_kills, gamelength_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (game_id, link) DO UPDATE SET
            team = excluded.team,
            role_number = excluded.role_number,
            date_time_utc = excluded.date_time_utc,
            overview_page = excluded.overview_page,
            kills = excluded.kills,
            deaths = excluded.deaths,
            assists = excluded.assists,
            cs = excluded.cs,
            gold = excluded.gold,
            damage_to_champions = excluded.damage_to_champions,
            vision_score = excluded.vision_score,
            player_win = excluded.player_win,
            team_kills = excluded.team_kills,
            gamelength_number = excluded.gamelength_number
    """,
    history_rows
)


# Save changes to the database
con.commit()

print(f"Done: {len(loaded_data)} games, {len(loaded_performances)} performances, "
      f"{len(triplets)} players, {len(history_rows)} history rows")

con.close()
