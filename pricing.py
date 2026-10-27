# Calculates player prices from history and writes them to players
# Used Claude (AI) for explaining SQL concepts (CASE, CTE)

import sqlite3
from helpers import WEIGHTS, points

# Connect to the database
con = sqlite3.connect("data/fantasy.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

# Extract: stats per player from history (small-league games count at 80%)
stats_per_player = cur.execute(
    """
        WITH history_with_factor AS (
            SELECT link, role_number, kills, deaths, assists, player_win, cs, damage_to_champions, vision_score, gamelength_number,
            CASE
                WHEN overview_page LIKE '%Asia Masters%'
                OR overview_page LIKE '%World Cup%'
                OR overview_page LIKE '%LCP%'
                OR overview_page LIKE '%LTA South%'
                OR overview_page LIKE '%VCS%' THEN 0.8
                ELSE 1.0
            END AS factor
            FROM history
        )
        SELECT link, role_number,
            COUNT(*) AS games,
            AVG(kills * factor) AS kills,
            AVG(deaths * factor) AS deaths,
            AVG(assists * factor) AS assists,
            AVG(CASE WHEN player_win = 'Yes' THEN 1 ELSE 0 END * factor) AS win,
            SUM(cs * factor) / SUM(gamelength_number) AS cs_per_min,
            SUM(damage_to_champions * factor) / SUM(gamelength_number) AS damage_per_min,
            SUM(vision_score * factor) / SUM(gamelength_number) AS vision_per_min
        FROM history_with_factor
        GROUP BY link, role_number;
    """
).fetchall()

# Finding the average game duration in minutes
average_gamelength = cur.execute("SELECT AVG(gamelength_number) FROM history").fetchone()[0]

# Transform: points per player in a standard game
players_points = []
for player in stats_per_player:
    standard_game = {
        "kills": player["kills"],
        "deaths": player["deaths"],
        "assists": player["assists"],
        "win": player["win"],
        "cs": player["cs_per_min"] * average_gamelength,
        "damage_to_champions": player["damage_per_min"] * average_gamelength,
        "vision_score": player["vision_per_min"] * average_gamelength
    }
    players_points.append({"link": player["link"], "role_number": player["role_number"], "points": points(standard_game)})

# Put each player's points in a list for their role
by_role = {}
for player in players_points:
    role = player["role_number"]
    if role not in by_role:
        by_role[role] = []
    by_role[role].append(player["points"])

# Average points for each role
average_by_role = {}
for role, points_role in by_role.items():
    average_by_role[role] = sum(points_role) / len(points_role)

# Compare each player's points with the average of their role
for player in players_points:
    role_average = average_by_role[player["role_number"]]
    player["points_vs_role"] = player["points"] - role_average

# Close connection
con.close()
