# Calculates player prices from history and writes them to players
# Used Claude (AI) for explaining SQL concepts (CASE, CTE)

import sqlite3

# Connect to the database
con = sqlite3.connect("data/fantasy.db")
cur = con.cursor()

print("Connected")

# Close connection
con.close()
