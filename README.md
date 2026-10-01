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

6. Run application
```
    flask run
```




