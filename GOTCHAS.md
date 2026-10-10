# Gotchas

Read these before joining, aggregating, or comparing across seasons.

## Identity

1. **Leaderboards have no player id.** Rows are `Last, First, Team, Division, …` only. Join to `players.csv`
   / `adda/player_crosswalk.csv` on `(league, season, Team, First + Last)`. Names are not unique — ADDA's own records have
   about 40 names shared by more than one record (some genuine namesakes, some duplicates awaiting a merge) — so join
   per season *and* team, never on name alone.
2. **`League Id` is not published.** DC's `players.csv` has a `League Id` column that was **meant to hold the ADDA
   player id**, but DC's values are unreliable and mutable (blank or wrong in some seasons, and DC will not let
   ADDA correct them). So it is dropped from the DartConnect files (README deviation 4) and the authoritative
   `adda_player_id` is published instead, via `adda/player_crosswalk.csv`. `ID` (the DCID) stays — it is the
   within-league join key to that crosswalk. `League Status` and `Season Status` are also not published
   (README deviation 5).
3. **DCIDs are per league.** The ~30 people in both leagues have a different `ID` in each. Within a league a
   DCID is stable across seasons, but the *name attached to it* is not always: e.g. `Buck Buckley` /
   `Gareth Buckley`, `Bryan` / `Brian Blase`. Match people by DCID, not by spelling.
4. **Team names change between seasons.** Always include the season when joining on team name.
5. **`zz Alternate zz` rows are shared placeholder accounts, not people** (ADDA only; several per team over
   the seasons). They appear in `players.csv` and in leaderboards. Exclude them from per-person analysis.
6. **`adda/` ids are ADDA's and are corrected over time** — see `adda/README.md`. The canonical name is in `adda/players.csv`; the crosswalk's `first`/`last` are the name as entered in DC that season (for the leaderboard join only) and may vary.

## What is (not) in the files

0. **Row order is ADDA's, not DC's.** Files are published in a deterministic sort (README "Row order") so that
   unchanged data gives unchanged files. Don't infer anything from a row's position; the cells are DC's as-is.

7. **Regular season only for leaderboards.** There are no post-season leaderboards; post-season exists only
   as `matchlog_post.csv`.
8. **`all_01` includes `singles_501`.** Do not add cuts together — you will double-count. `all_cricket`
   includes `singles_cricket`. `leaderboard_match_record` (DC's `all` cut) is sets/legs/match record, not "all games".
9. **Blank metrics mean "did not play this cut", not zero.** A player with a blank `Matches` in
   `singles_cricket` is real and active; they just did not throw singles cricket.
10. **`players.csv` is DC's season roster snapshot, active rows only** — what was in DartConnect during that season's active window; mutable and point-in-time, not canonical. Rows with no Team or no Division were dropped — see the README
    ledger. (The blank-Team/Division rule runs on `players.csv` **and** the leaderboards; it currently drops 0
    leaderboard rows.) Two kinds exist in DC's export: registered players with no team that season, and rows that carry a
    Team but a blank Division. In every season, neither kind appears in that season's leaderboards, and every
    leaderboard player is in the published roster. The converse is not true: the roster also lists players who
    played no games that season, so `players.csv` is a roster, not a list of participants.
11. **`Position` is always blank** in DC's roster export, all seasons and both leagues. It carries no
    gender or lineup information. (The build refuses to publish a non-blank value without review.)
12. **`Venue` is a bar/venue name**, never a street address (every published value is a venue name).
13. **For gender, use `adda/players.csv`**, which publishes `gender` for every player in both leagues (`M`/`F`, occasionally `U`; blank = not recorded). DC's own
    `Gender` column is also kept, as DC has it, in both leagues' roster and leaderboard files under `dartconnect/`, but it is a per-season snapshot: it is
    sometimes `U` or blank where the canonical value is known, and occasionally differs from it. Treat either as a registration field, not a verified attribute.

## Seasons and cuts

14. **ADDA Winter/Spring 2025 (season 59) has two sets of leaderboards** because Division D played a longer
    regular season. `…__div_ABC.csv` (through 2025-04-05) is authoritative for divisions A/B/C;
    `…__div_D.csv` (through 2025-04-25) is authoritative for D. **Each file contains all divisions**; the
    other divisions' rows in each file cover a different window than their own regular season — take a
    division's rows only from its authoritative file (`division_scope` in the manifest).
15. **Folder / label mismatches.** ADDACL season 24's DC label is "Winter/Spring 2025" (the archive folder is
    `addaclSummer2025`). The published key is always the season number. ADDA 59's DC label is also
    "Winter/Spring 2025" — labels are not unique across leagues, season numbers are (per league).
16. **Fall 2026 (ADDA 64, ADDACL 27) is in progress.** No `matchlog_post.csv`; leaderboards and rosters are
    partial and will change (`status: "in_progress"` in the manifest).
17. **`archived_at` is not the DC export time.** Most files were archived in a single backfill on 2026-05-01;
    it is the date ADDA archived the file.
18. **Era boundary.** ADDA 57 and ADDACL 23 are the first DC-era seasons; this corpus does not include, and
    should not be merged naively with, the pre-DC (legacy) data on addadarts.com. A `legacy/` directory is reserved for that data (see the README); it does not exist yet.

## Columns and formats

19. **Read columns by name, never by position.** Header drift: a `Best Leg` column appears between `HDO` and
    `100+` in the 01 leaderboards from ADDA 63 (Summer 2026) and ADDACL 27 (Fall 2026) onward; earlier files
    lack it and later columns shift. Column order also differs between cuts (`Legs`/`Matches` swap in
    `match_record`).
20. **Match-log oddities.** One column has an *empty header name* (between `DER` and `Report Link`) and is
    always blank. Quoting style differs by file: the older
    `-POST` logs (ADDA 57–61, ADDACL 23–25) are entirely unquoted, everything else is fully quoted. `Start Time` /
    `End Time` have unpadded minutes (`20:6` = 20:06): **pre-pad the minutes field yourself; do not feed the value to a
    standard time parser** (`22:6` is not a valid `HH:MM` and may be misread). Scores are strings like `03 @ 10`. Dates are `m/d/yyyy`.
21. **Forfeits and manual entries.** Rows with `Source = League Portal` and a blank `Report Link` are
    forfeits or hand-entered results: no throw data, so they are absent from the leaderboards but present in the
    match log (ADDACL season 23: 15 of 78 regular-season rows). Every row with `Source = Scoring App` has a recap link.
22. **Recap links** (`recap.dartconnect.com/history/report/match/<id>`, and in two rows an `…/report/event/<id>`
    `Event Link`) are DC's public recap pages and are published as-is.
23. **Doubles Shanghai (ADDACL).** DC cannot score it. Leaderboard `Swon` / `Match Wins` omit it, while match-log
    `Set Score` and `League Points` include it. Coed leaderboard totals therefore will not reconcile to the match log.
24. **Ties and `Set Win%`.** `STied` and `Match Ties` columns exist. Determined empirically: `Set Win% = 100 × Swon / Sets`
    on every row in the corpus (1,692), and `Sets = Swon + STied + Set Losses` — so **a tied set counts in `Sets`
    but as zero wins, not half a win**. Caveat: only 2 rows in the corpus have a non-zero `STied` (both ADDA
    Summer 2024, e.g. `Sets 39, Swon 25, STied 1, Set Losses 13, Set Win% 64.1` = 25/39, where half-credit would
    give 65.38), so the tie rule rests on those two rows. `Match Wins` / `Match Ties` are blank in every row.
25. **Name variants.** A few DCIDs carry a different name than ADDA's records (e.g. DC `Buck Buckley` vs
    ADDA `Gareth Buckley`); `adda/player_crosswalk.csv` resolves these by DCID and says so in its `note` column; the canonical name is in `adda/players.csv`.
26. **Same column name, different meaning across cuts.** `Legs Win` is a **percentage** (two decimals, `47.06`) in the
    01 and cricket leaderboards (`100 × LWon / Legs`) but a **count** of legs won in `leaderboard_match_record`
    (where the percentage is `LW%`). `Legs` and `Matches` are per-cut in the 01/cricket files but cover all game
    types in `match_record`, and their column order swaps there. `Season` in the match logs is the phase
    (`REG`/`POST`), not a season. `League ID` in the match logs is the league code (`ADDA`), unrelated to the
    (unpublished) `players.csv` `League Id`. `Division` labels differ between regular and post-season logs
    (`A` vs `Division A`, plus cup names). See `COLUMNS.md`.
27. **No per-player matchup detail in the export.** This is a Dart Connect limitation: results are team-level.
    Per-match and per-leg opponent detail (who threw against whom) is only available behind the recap links in the
    match logs (`Report Link`); see [`RECAPS.md`](RECAPS.md) for how to read those pages (they are Dart
    Connect's — mind their terms and rate limits).
28. **How long a match took: neither `Duration` nor `End Time − Start Time` is reliable on its own.** `Duration`
    is the time each set took, added up — not elapsed time. Sets run at the same time on different boards, so on a
    normal night `Duration` is *longer* than `End Time − Start Time` (median +36 minutes). Two kinds of outlier,
    out of 1,324 matches with times (as of October 2026):
    - **`End Time` earlier than `Start Time` (45 matches):** the match was closed on a later day, and the log gives
      no end date, so the elapsed time can't be computed (e.g. ADDACL 27, 9/10/2026, ATLiens @ Recovering Catholics:
      `20:8` to `11:40`, `Duration` 98).
    - **`Duration` over 10 hours (15 matches, 10 of them also closed on a later day):** most likely a set left open
      in the app, whose time kept counting — up to 60,530 minutes, about 42 days (ADDA 59 post-season, 4/7/2025,
      Inner Voice @ Off in the Woods). The per-leg clocks on its recap page add up to far less.

    For elapsed time, use `End Time − Start Time` when the end is later than the start; for playing time, use
    `Duration`, but check it is plausible first. `League Portal` rows (#21) have no times, `Duration` or `DER` at all.
