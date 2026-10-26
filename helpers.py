# Shared helpers for the fantasy app: scoring weights and the scoring function
# Used Claude (AI) for explaining the weights approach.

# Points for each stat. I use the same numbers for prices and for scoring.
WEIGHTS = {
    "kills": 5,
    "deaths": -2,
    "assists": 2,
    "cs": 0.07,
    "damage_to_champions": 0.0006,
    "vision_score": 0.2,
    "win": 33
}

# Adds up the points for one game.
def points(stats):
    total = 0
    for stat, weight in WEIGHTS.items():
        total += weight * stats[stat]
    return total
