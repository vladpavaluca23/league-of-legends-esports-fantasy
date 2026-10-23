# League of Legends Esports Fantasy

A fantasy league web app for LoL esports. Users draft a team of five pro players on a budget and score points from real match stats pulled from Leaguepedia.

Work in progress — CS50x Final Project.

# How to run

1. Clone the repository
```
    git clone https://github.com/vladpavaluca23/league-of-legends-esports-fantasy.git
```

2. Change directory
```
    cd league-of-legends-esports-fantasy
```

3. Create environment
```
    python -m venv .venv
```

4. Activate the virtual environment:

   - **Windows (PowerShell):**

     ```
     .venv\Scripts\Activate.ps1
     ```
     > On Windows, if you get a "running scripts is disabled" error, run this once:
     >  `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`


   - **macOS / Linux:**

     ```
     source .venv/bin/activate
     ```

5. Install requirements
```
    pip install -r requirements.txt
```
6. Add your Leaguepedia credentials

   Create a bot password at https://lol.fandom.com/wiki/Special:BotPasswords
   (with Cargo permissions), then create a `.env` file in the project folder:
```
    LEAGUEPEDIA_USER=YourAccount@YourBotName
    LEAGUEPEDIA_PASSWORD=your_bot_password
```

7. Download the data
```
    python ingest.py
```
   Raw data is not included in the repo. This saves it into `data/`.
   It takes about 2 minutes, because the player history is fetched one player at a time.

   Running `ingest.py` also creates the SQLite database `data/fantasy.db`
with four tables: games, players, performances and history.

8. Run application
```
    flask run
```

## Design decisions

- Player prices come from games before the Main Event. Prices are based on each player's last `N_GAMES` (20) games played before the first Main Event game, Play-In included.

- Player links are normalized. While checking the data, I found a player written as `Shad0w` in the Worlds data and `shad0w` in his earlier games. During ingestion, every link in `history` is rewritten to its spelling in `players`.
- Prices are calculated in `pricing.py`, separate from `ingest.py`, so all pricing rules stay in one place.
- A price is a guess of how many fantasy points a player will score, so it uses the same stats and weights as the scoring engine: kills, deaths (small penalty), assists, CS, damage, vision and wins. CS, damage and vision are counted per minute, because they grow with game length. Games from smaller leagues count at 80%. Each player is compared only with players in the same role.
- Left out on purpose: a minimum number of games and a default price, because all 83 players have 20 games in the pricing window.

## Known limitations

- **Renamed players.** Players are identified by their Leaguepedia `link`.
  If a player changes their in-game name, they show up as a separate player for every name they used.
  This is acceptable for now because a name change during a single tournament is very unlikely.
  A fix would be to map every old name to the same player, using a source that tracks name history.

- **One role and one team per player.** The ingestion assumes that every player has exactly one role and one team.
  If the data shows the same player with more than one role or team, the script stops instead of saving anything.
  This is on purpose: at Worlds, rosters are locked, so a conflict most likely means the data is corrupted.
  Tracking these changes would need a role and team history for each player, with start and end dates.

- **The pricing window covers different time spans.** Every player gets the same number of games (20), no matter when they were played.




