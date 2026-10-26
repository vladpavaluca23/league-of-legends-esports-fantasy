# Calculates player prices from history and writes them to players
# Used Claude (AI) for explaining SQL concepts (CASE, CTE)

import sqlite3
from helpers import WEIGHTS, points

# Connect to the database
con = sqlite3.connect("data/fantasy.db")
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

# Close connection
con.close()
