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

   Running `ingest.py` also creates the SQLite database `data/fantasy.db`
with three tables: games, players and performances.

8. Run application
```
    flask run
```
## Known limitations

- **Renamed players.** Players are identified by their Leaguepedia `link`.
  If a player changes their in-game name, they show up as a separate player for every name they used.
  This is acceptable for now because a name change during a single tournament is very unlikely.
  A fix would be to map every old name to the same player, using a source that tracks name history.

- **One role and one team per player.** The ingestion assumes that every player has exactly one role and one team.
  If the data shows the same player with more than one role or team, the script stops instead of saving anything.
  This is on purpose: at Worlds, rosters are locked, so a conflict most likely means the data is corrupted.
  Tracking these changes would need a role and team history for each player, with start and end dates.




