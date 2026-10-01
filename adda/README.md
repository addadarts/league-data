# adda/ — ADDA's canonical layer and the DC → ADDA crosswalks

**ADDA's own data. Not Dart Connect data.** Built from ADDA's canonical player/team records and the same
`players.csv` rows published under `dartconnect/`. This is the part of the corpus that spans sources: it is how
a row in a DartConnect file is tied to a person or team on addadarts.com (see the top-level README for the link recipe).

**As of** the date in the `as_of` column / `manifest.json` → `adda.as_of`. It **may be corrected on future merges**
(ADDA merges duplicate person records). Rows that could not be matched are published as unresolved / ambiguous —
never guessed. Every id column is the **first** column of its file.

## Files

| File | Rows |
|------|------|
| `players.csv` | **Canonical.** Exactly one row per `adda_player_id`: `adda_player_id, name, gender`. The correct/current name lives here. Gender is published for all players (both leagues; blank = not recorded). |
| `teams.csv` | **Canonical.** Exactly one row per `adda_team_id`: `adda_team_id, name, league, current_venue`. `name` is the current (most-recent-season) name; `current_venue` is the venue **as of the team's latest season**. |
| `player_crosswalk.csv` | One row per **published** `dartconnect/…/players.csv` row, **both leagues combined** (`league` column). |
| `team_crosswalk.csv` | One row per (league, season, DC team, division) in those rosters, both leagues combined. |

Scope: `players.csv` and `teams.csv` contain **only the ids referenced by the crosswalks** (not every record ADDA holds).

Referential integrity: every `adda_player_id` in `player_crosswalk.csv` exists in `players.csv`, and every
`adda_team_id` in either crosswalk exists in `teams.csv` (the build fails otherwise).

## Canonical name vs. season name

`players.csv` holds the correct/current name. The crosswalk's `first` / `last` are the name **as entered in DC that
season** — kept only so leaderboard rows (which carry names, not ids) can be joined, and they may vary between
seasons or from the canonical name. Use `players.csv` for display.

## `player_crosswalk.csv` columns

| Column | Meaning |
|--------|---------|
| `adda_player_id` | canonical ADDA player id (blank when not resolved) |
| `league`, `season_num`, `dc_season_id` | ADDA / ADDACL, ADDA season number, DC's season id |
| `dc_id` | DC `ID` from the season's `players.csv` — the join key (per league) |
| `first`, `last` | name as entered in DC that season (for the leaderboard join only; see above) |
| `dc_team`, `division` | as in `players.csv`, so leaderboard rows can be joined by name + team |
| `adda_team_id` | canonical ADDA team id (blank when not resolved) |
| `match_method` | `dcid` (DC id equals the canonical record's DC id), `name+team` (name found on the canonical team roster for that season), `none` |
| `status` | `resolved`, `ambiguous` (conflicting or multiple candidates — see `note`), `unresolved`, `placeholder` |
| `note` | why a row is not a plain match (e.g. `dcid match; name not on canonical team roster for season`) |
| `as_of` | date the crosswalk was built |

`status = placeholder` marks DC's shared "zz Alternate zz" accounts. They carry an id when the DC id
maps to one, but they are not people and have no player page.

## `team_crosswalk.csv` columns

`adda_team_id, league, season_num, dc_season_id, dc_team, division, dc_season_team_id, match_method
(name | name(previousNames)), status, note, as_of`. `dc_season_team_id` is DC's team-season id where
ADDA has it on record (blank for older seasons).
