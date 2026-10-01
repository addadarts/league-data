# ADDA / ADDACL league data (Dart Connect exports)

Season-by-season CSV exports for the **Atlanta-Decatur Dart Association** leagues, as produced by
[Dart Connect](https://dartconnect.com) (DC):

- **ADDA** — the Monday league, seasons 57–64 (Summer 2024 → Fall 2026)
- **ADDACL** — the Coed league, seasons 23–27 (Fall 2024 → Fall 2026)

The season files are Dart Connect's. ADDA archives DC's exports and publishes them under `dartconnect/` **as-is except for the six
deviations below**. ADDA's own canonical layer — canonical players and teams, and the crosswalks that tie DC's rows to them — is [`adda/`](adda/README.md).
Start with [`manifest.json`](manifest.json) (one fetch lists every file with its league, season, cut,
date range, row counts, checksums and which columns/rows were removed), and read
[`GOTCHAS.md`](GOTCHAS.md) before computing anything; [`COLUMNS.md`](COLUMNS.md) defines the columns (including [ADDAs](COLUMNS.md#addas), ADDA's own high-score-turn measure, from the live [season-stats FAQ](https://addadarts.com/season-stats)), and [`RECAPS.md`](RECAPS.md) explains how to read the
per-match recap pages the match logs link to (where per-leg / per-turn detail lives).

## Structure: `dartconnect/` vs `adda/` (and a reserved `legacy/`)

The corpus is split by **who the data belongs to**:

- **`dartconnect/`** — DC's raw, per-source exports, one folder per league and season. Content is DC's (the six
  deviations are removals only). It is a *source* layer: point-in-time, mutable, and not ADDA's to license.
- **`adda/`** — ADDA's own canonical layer, spanning sources: one canonical row per player and per team, plus the
  crosswalks from each DC season row to those canonical ids. This is the part that is actually ADDA's to license.
- **`legacy/`** — **reserved, not present yet.** Pre-DartConnect data (the old platform was literally called "Legacy")
  will land here as another per-source layer, mapped to the same `adda_player_id` / `adda_team_id` in `adda/`.

```
manifest.json                       discovery + checksums
GOTCHAS.md                          read this before you aggregate anything
COLUMNS.md                          column dictionary (what each published column means, and how sure we are) + the ADDAs methodology
RECAPS.md                           how to read the public Dart Connect recap pages the match logs link to
dartconnect/{adda,addacl}/{season_num}/          DartConnect's season exports (source layer)
    players.csv                     DC's season roster snapshot (active rows only, contact info removed)
    leaderboard_singles_501.csv     DC leaderboard cuts — regular season only
    leaderboard_all_01.csv
    leaderboard_singles_cricket.csv
    leaderboard_all_cricket.csv
    leaderboard_match_record.csv    DC's "all" cut: sets / legs / match record
    matchlog_reg.csv                DC match log, regular season (includes recap links)
    matchlog_post.csv               DC match log, post-season (completed seasons only)
adda/                               ADDA's canonical layer (not DC data)
    players.csv                     CANONICAL: 1 row per adda_player_id — name, gender (all players)
    teams.csv                       CANONICAL: 1 row per adda_team_id — current name, league, current_venue
    player_crosswalk.csv            per-(league, season) DC player rows -> adda_player_id (both leagues)
    team_crosswalk.csv              per-(league, season) DC teams -> adda_team_id (both leagues)
legacy/                             RESERVED — future pre-DartConnect data (not built yet)
```

### What `dartconnect/…/players.csv` is (and is not)

It is **DC's season-specific roster snapshot**: what was in DartConnect during that season's active window. Use it
to (a) match leaderboard rows to an `adda_player_id` through `adda/player_crosswalk.csv`, and (b) read the season's
team → division, team → venue and team → captain assignments. It is **not** canonical or authoritative — it is
mutable, point-in-time data. For who a person *is* (name, gender, id), use `adda/players.csv`.

### Canonical name vs. season name

`adda/players.csv` holds the correct/current name. The crosswalk's `first` / `last` — like `First Name` / `Last Name`
in `players.csv` — are the name **as entered in DC that season**; they exist for the leaderboard join and may vary.

`season_num` is the ADDA season number (not the archive folder name). ADDA Winter/Spring 2025 (season 59)
has two sets of leaderboards, `…__div_ABC.csv` and `…__div_D.csv` — see GOTCHAS. Seasons whose
`status` in the manifest is `in_progress` (currently ADDA 64, ADDACL 27) are partial and will change.

## The six deviations from Dart Connect's files

Everything else — column order, quoting, values, line endings — is DC's, byte for byte. Rows and columns
are only ever *removed*, never edited or reordered. The build refuses any
input whose header contains a column it does not recognise.

| # | Deviation | Applies to | Effect |
|---|-----------|-----------|--------|
| 1 | Contact info removed: `Email`, `Phone` | `players.csv`, all leagues (only file that has them) | columns removed |
| 2 | `Country` removed | `players.csv` + leaderboards, all leagues | column removed |
| 3 | `Gender` removed | **ADDA only** (players + leaderboards). **Kept for ADDACL** (coed) | column removed |
| 4 | Inactive rows dropped: blank `Team` **or** blank `Division` | `players.csv` **and** the leaderboards (the rule runs on both; it currently drops 0 leaderboard rows). In `players.csv` these are registered-but-not-playing rows that season | rows removed |
| 5 | `League Id` removed | `players.csv`, all leagues. `ID` (the DCID) is kept. The [`adda/`](adda/README.md) crosswalk is the single authoritative source of canonical ids | column removed |
| 6 | `League Status` and `Season Status` removed | `players.csv`, all leagues. These are league-administration fields (they can record that a player is restricted from playing) and are not published | columns removed |

Machine-readable: `manifest.json` → `deviations` lists all six (`league_id_column_dropped` is the fifth, `league_status_season_status_columns_dropped` the sixth).
Each manifest entry lists `columns_removed`, `rows_in` (DC's row count) and `rows_out` (published).
Rows with a blank `Matches` value in a leaderboard cut are **kept** — they are players who did not play
that cut, not inactive players. Match logs are published unchanged (recap links included).

## IDs, and how to link a row to addadarts.com

| Field | Where | What it is | Use it as a key? |
|-------|-------|------------|------------------|
| `ID` (the "DCID") | `players.csv` | DC's player-account id, **per league** (the same person has different DCIDs in ADDA and ADDACL) | **Yes, within one league** — stable across seasons; the join key between `players.csv` and the crosswalk |
| `League Id` | *(not published)* | DC's column that was **meant to hold the ADDA player id**; DC's values are unreliable and mutable (blank or wrong in some seasons), so it is dropped from the DC files and the authoritative id is published instead (deviation 5) | **No — use `adda_player_id` from `adda/player_crosswalk.csv`.** |
| `adda_player_id` | `adda/players.csv` (canonical), `adda/player_crosswalk.csv` | ADDA's canonical player id (one per person, spans both leagues and pre-DC history) | Yes — this is the id addadarts.com uses |
| `adda_team_id` | `adda/teams.csv` (canonical), both crosswalks | ADDA's canonical team id | Yes |

The leaderboards have **no player id** — rows are `Last, First, Team, Division…`. To get from a leaderboard
row to an id, join on `(league, season, Team, First + Last)` to that season's `players.csv` /
`adda/player_crosswalk.csv` row (in the build this joined every one of the ~1,700 `all_01` leaderboard rows).

**To build an addadarts.com link**

1. Take the player's row in `adda/player_crosswalk.csv` (match on
   `league`, `season_num`, `dc_id` — the `ID` from `players.csv`).
2. Only use rows with `status = resolved` (skip `ambiguous`, `unresolved`, and `placeholder` — the latter are DC's
   shared "zz Alternate zz" accounts, not people; the site's team pages hide them).
3. Player page: `https://addadarts.com/player-cards?id={adda_player_id}`
   Team page: `https://addadarts.com/team-cards?id={adda_team_id}`

(These URL shapes are what addadarts.com uses at `as_of` in the manifest; the site can change them.)

**`adda/` is ADDA's own data, not Dart Connect data, and is `as_of` a date** (column `as_of`,
and `adda.as_of` in the manifest). ADDA merges duplicate person records over time, so an
`adda_player_id` may be corrected in a later build. Unresolved and ambiguous rows are published as
such; nothing is guessed. Re-fetch before relying on a stored id for anything long-lived.

## Questions & Discussion

Open an [**Issue**](../../issues) on this repository — it is the right place for:

- **Field meanings and how-to questions** ("what does this column mean?", "how do I join these files?")
- **Data-quality reports** (numbers that look wrong, missing rows, mismatches with what you saw on a recap page)
- **Player-data problems** (a player or team linked to the wrong person or team, a name that needs correcting)

Anyone with a GitHub account can post. Issues are public, so please don't include private contact details.
Templates are provided, but a blank issue is fine too.

## How to cite

> Dart Connect league exports for the Atlanta-Decatur Dart Association (ADDA / ADDACL), archived and
> published by ADDA. `<repository URL>`, commit `<hash>`, manifest `as_of` `<date>`. Source: Dart Connect,
> https://dartconnect.com (terms: https://www.dartconnect.com/league-administrator-updates/export-leaderboard/).

Cite the specific season(s) and `sha256` from the manifest if reproducibility matters.

## License / terms

**`dartconnect/` — Dart Connect's data; no ADDA license.** Source data © Dart Connect, republished under Dart
Connect's export "other purposes" clause ([DartConnect's export-leaderboard page](https://www.dartconnect.com/league-administrator-updates/export-leaderboard/)); no additional rights
are granted by ADDA over the underlying Dart Connect data. ADDA is not the rights-holder of that data and
does not license it. Its removals (the six deviations) are the only changes ADDA made.

**`adda/` — ADDA's own data.** The canonical players/teams files and the crosswalks are ADDA's work and ADDA's to license; together with the documentation
(`README.md`, `GOTCHAS.md`, `COLUMNS.md`, `RECAPS.md`, `adda/README.md`) they are published under
[**Creative Commons Attribution 4.0 International (CC BY 4.0)**](https://creativecommons.org/licenses/by/4.0/).
Credit ADDA and Dart Connect per "How to cite" above. (The `adda/` files contain no Dart Connect-sourced values
beyond the DC ids and names needed to join to them.)

If your use goes beyond typical league-stat browsing or hobby analysis, confirm with Dart Connect first.
