-- Exploration queries behind the pricing decisions. Run them on data/fantasy.db.
-- Used Claude (AI) for explaining "CASE" and "CTE" SQL concepts.

-- 1. Average stats per player per game in history
-- Result: kills 3.1, deaths 2.7, assists 7.9, cs 222.2, damage 17907.2, vision 56.3, win 62.0%
SELECT
    ROUND(AVG(kills), 1) AS kills,
    ROUND(AVG(deaths), 1) AS deaths,
    ROUND(AVG(assists), 1) AS assists,
    ROUND(AVG(cs), 1) AS cs,
    ROUND(AVG(damage_to_champions), 1) AS damage,
    ROUND(AVG(vision_score), 1) AS vision,
    ROUND(AVG(CASE WHEN player_win = 'Yes' THEN 1 ELSE 0 END) * 100, 1) AS win_pct
FROM history;

-- 2. Average game length in history, in minutes (the standard game for per-minute stats)
-- Result: 32.8
SELECT ROUND(AVG(gamelength_number), 1) AS avg_minutes
FROM history;

-- 3. League factor per tournament (games from small leagues count at 80%)
-- Result: 7 of 18 tournaments get 0.8 (LCP x3, VCS, LTA South, Asia Masters, Esports World Cup)
SELECT DISTINCT overview_page,
	CASE
		WHEN overview_page LIKE '%Asia Masters%'
		OR overview_page LIKE '%World Cup%'
		OR overview_page LIKE '%LCP%'
		OR overview_page LIKE '%LTA South%'
		OR overview_page LIKE '%VCS%' THEN 0.8
		ELSE 1.0
	END AS factor
FROM history
ORDER BY overview_page;
