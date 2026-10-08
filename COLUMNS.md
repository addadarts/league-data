# Column dictionary

One line per column of the published files, best-effort. **Dart Connect (DC) does not document its export
columns**, so every line carries a confidence tag:

- **[verified]** — a formula or identity was checked against every row in the corpus (stated in the line);
- **[inferred]** — meaning taken from the column's name and its values; consistent with the data but not checked against a DC definition;
- **[unknown]** — we do not know what this is. Do not build on it without asking DC.

Where a line says "checked", the relationship was tested against the rows of this corpus stated in that line.
Where it says **ADDA re-implements** a stat, ADDA computes the same figure itself from DC's per-turn data, so
that definition is ADDA's working understanding of the column, not a DC document. Turn-level checks below were
made by recomputing each figure from DC's public per-turn recap data (see `RECAPS.md`) for every ADDA and ADDACL
season with recap data on hand (ADDA Summer 2024 → Fall 2026; ADDACL Fall 2024 → Fall 2026) and comparing with the
leaderboard value of the `all_01` / `all_cricket` cuts; they cover only the players whose own totals could be
reproduced exactly from the recap data (`Darts Thrown` and `Points Scored` for 01 — 779 `all_01` rows; `Marks Scored`
for cricket — 262 `all_cricket` rows; the remaining rows differ through name variants, score edits and missing recaps,
so they were not used as evidence either way). "Checked on N rows" below always means those rows.

ADDA's own use of these columns (the "ADDAs" high-score-turn measure) is explained in [ADDAs](#addas) at the end.

Headers below are quoted exactly as they appear in the files. Read columns **by name, not position** (GOTCHAS #19).
Blank cells mean "no value" — for the leaderboards that means the player did not play that cut (GOTCHAS #9).

## `dartconnect/…/players.csv` (DC's season roster snapshot)

DC's **season-specific roster snapshot** — what was in DartConnect during that season's active window. It is mutable, point-in-time data, **not** the canonical player record (that is [`adda/players.csv`](#adda-canonical-files)).

Header as published: `"ID","First Name","Last Name","Division","Team","Captain","Venue","Position"`
(ADDACL's file also has `"Gender"` between `"Venue"` and `"Position"`; ADDA's does not — gender for every player is in `adda/players.csv`. Removed columns are listed in the README's deviation ledger.)

| Column | Meaning |
|--------|---------|
| `ID` | DC's player-account id ("DCID"), per league, stable across seasons. The join key to `adda/player_crosswalk.csv`. **[verified]** unique per person within a league's crosswalk (no DCID maps to more than one ADDA id). |
| `First Name`, `Last Name` | Name as entered in DC that season (may differ from the canonical name in `adda/players.csv`). **[verified]** |
| `Division` | The player's division that season (`A`–`E`, or `Coed`). **[inferred]** |
| `Team` | Team name that season. **[verified]** (matches the leaderboards' `Team`) |
| `Captain` | `Captain` / `Co-Captain` / blank. **[inferred]** |
| `Venue` | The team's home venue name (GOTCHAS #12). **[inferred]** |
| `Gender` | ADDACL files only (`M`/`F`/`U`/blank); for all players in both leagues see `gender` in `adda/players.csv`. **[inferred]** registration field. |
| `Position` | Always blank (GOTCHAS #11). **[verified]** |

`League Id` is deliberately **not published** (README deviation 4): use `adda_player_id` from `adda/player_crosswalk.csv`. `League Status` and
`Season Status` are also **not published** (README deviation 5).

## Leaderboards — shared by the four 01/cricket cuts

Cuts: `singles_501` (DC `Singles_501_SI_DO`), `all_01`, `singles_cricket`, `all_cricket`. One row per player.

| Column | Meaning |
|--------|---------|
| `Last`, `First`, `Gender`, `Team`, `Division` | Identity/team of the row. `Gender` only for ADDACL. No player id — GOTCHAS #1. **[verified]** |
| `Matches` | Matches the player played in this cut. **[inferred]** |
| `Legs` | Legs played in this cut. **[verified]**: `LWD + LAD = Legs` on all 3,313 01-cut rows. |
| `LWon` | Legs won. **[verified]**: `LWD Wins + LAD Wins = LWon`; `Legs Win = 100 × LWon / Legs`. |
| `Legs Win` | **Percentage** of legs won, 2 decimals (`47.06`). **[verified]** on every 01 and cricket row. *(In the `match_record` cut the same name is a count — GOTCHAS #26.)* |
| `LWD` | Legs played "with darts" — i.e. the player throwing first. **[inferred]** from the name; only `LWD + LAD = Legs` is verified. |
| `LWD Wins` | Of those, legs won. **[verified]** (`WD% = 100 × LWD Wins / LWD`) |
| `WD%` | Win % in `LWD` legs. **[verified]** |
| `LAD` | Legs played "against the darts" — opponent throwing first. **[inferred]** (see `LWD`) |
| `LAD Wins`, `AD%` | Legs won in `LAD`; win %. **[verified]** (`AD% = 100 × LAD Wins / LAD`) |
| `Darts Thrown` | Darts thrown in this cut. **[inferred]**; consistent with `3DA` and `MPR` below. |

### 01 cuts (`singles_501`, `all_01`) — additional columns

Turn-level columns are defined in terms of a player's **turns** (one visit of up to three darts). A bust scores 0
points for that turn. In the `all_01` cut, doubles and team legs are included and each turn is attributed to the
player who threw it (the recap's `name`), so the figures are per person.

| Column | Meaning |
|--------|---------|
| `Points Scored` | Total points scored. **[inferred]**; consistent with `3DA` and with the per-turn recap totals (see `3DA`). |
| `3DA` | Three-dart average. **[verified]**: `3 × Points Scored / Darts Thrown` on all 3,313 rows; and `Points Scored` / `Darts Thrown` were reproduced exactly from recap turns (a bust turn is 0 points and 3 darts; a finishing turn counts only the darts actually thrown) for the 321 `singles_501` and 301 `all_01` player rows used in the checks below. |
| `O-3DA` | **Opponent three-dart average** — the 3DA compiled from the turns thrown by this player's *opponents* in the legs this player played (how well opponents scored against them): `3 × Σ opponents' points / Σ opponents' darts`, over the same legs as the player's own `Darts Thrown`. In doubles legs the opponents are the other side's players. **[verified]**: matched the leaderboard value to within rounding (±0.005) for **every** row tested — 321 of 321 `singles_501` and 301 of 301 `all_01` rows. The alternative reading — the *average of the opponents' own overall season 3DAs* — was tested on the same rows and matched **0** of them (mean absolute error about 4 points), so it is ruled out. |
| `First 9` | Average over the first nine darts of a leg (3-dart-average scale). **[inferred]** |
| `HTurn` | Highest single-turn score (points in one three-dart turn). **[verified]**: equals the player's highest recap turn score in 779 of 779 `all_01` rows tested. `HSI`, `HDIT`, `HDI`, `HDO` are all ≤ `HTurn` on every row where both are present. |
| `HSI` | **Highest first turn in straight-in legs** (`inMode = straight`: Singles 501 and Team 801 — no double needed to start scoring). **[verified]**: equals the highest score of any player's *own first* turn of a leg over Singles 501 + Team 801 legs in 779 of 779 `all_01` rows tested (Singles 501 alone matches only about half, so Team 801 is part of the definition; in 801 every player's own first turn counts, not just the side's first). |
| `HDIT` | **Highest double-in turn** — counts a double-in **whenever it happens** (on any turn of the leg). In double-in legs (Doubles 301), it is the highest score of the turn on which a **pair first scored** (the side's first non-zero turn; missed double-ins score 0), credited to the partner who threw it. This is the column ADDA's website calls "High In" (see [ADDAs](#addas)). **[verified]**: equals that figure in 779 of 779 `all_01` rows tested. Variants using each player's own first turn, or only the partner who threw the leg's opener, matched far fewer rows. Blank for players with no double-in leg (and `HDI` is blank in exactly the same rows — all 3,384 rows). |
| `HDI` | **Highest double-in scored on the first turn** — like `HDIT`, but counts only double-ins that happen on the **first turn**, where `HDIT` counts them on any turn. **[inferred]**: the owner's definition, and the data is consistent with it but does not reproduce it exactly. Checked on the 628 tested rows that have a double-in: `HDI ≤ HDIT` on **all 628** (and on all 1,433 corpus rows where both are present; equal to `HDIT` in 890 of them, which is what you expect when a player's best double-in came on a first turn); in 485 of the 628 `HDI` equals the highest score of a double-in turn thrown on that player's *own* first turn of the leg. In the other 143 rows (mostly players whose double-ins came on a later turn) `HDI` is still populated with a smaller value that we could not match to any single rule (often about half of `HDIT`), so the exact first-turn rule is not fully reproduced. |
| `HDO` | **Highest out** — the highest score of a **finishing (checkout) turn**. This is the column ADDA's website calls "High Out" (see [ADDAs](#addas)). **[verified]**: equals the player's highest recap checkout-turn score in 778 of 779 `all_01` rows tested (1 exception, cause not determined). `Avg Fin` ≤ `HDO` ≤ `HTurn` wherever present. |
| `Best Leg` | Best (fewest-darts) leg. **[inferred]**; present only from ADDA 63 / ADDACL 27 on (GOTCHAS #19). |
| `100+`, `140+`, `180` | Counts of turns scoring 100+, 140+, and 180. **[inferred]** |
| `Ton Points` | **[inferred]** total points scored in turns of 100 or more. Checked: `100 × (100+) ≤ Ton Points ≤ 180 × (100+)` and `Ton Points = 0` exactly when `100+ = 0`, on all 2,631 rows with values (`singles_501` + `all_01` cuts). It is **not** `100+` itself. |
| `T95_113`, `T14_32`, `T33_51`, `T52_70`, `T71_80` | **The 19-based turn-score buckets — the ones ADDA uses.** Counts of turns whose total score falls in a band: `T95_113` = 95–113, `T14_32` = 114–132, `T33_51` = 133–151, `T52_70` = 152–170, `T71_80` = 171–180 (the leading `1` of the three-digit edges is dropped in the names: `T14_32` = 114–132; each band is 19 wide). A turn lands in at most one band; turns below 95 are in none. **[verified]**: each column equals the count of recap turns in exactly that range on 779 of 779 `all_01` rows (all five columns, every row). A 180 is counted in `T71_80` (and also in `180`). These feed ADDA's '01 ADDAs formula — see [ADDAs](#addas). |
| `T00_19`, `T20_39`, `T40_59`, `T60_79` | **The 20-based turn-score buckets — a second, parallel bucketing, not used by ADDA.** DC provides these too, for leagues that bucket by multiples of 20: `T00_19` = 100–119, `T20_39` = 120–139, `T40_59` = 140–159, `T60_79` = 160–179 (names drop the leading `1`, so `T00_19` is 100–119 — it is **not** a lower band of `T95_113`). **[verified]**: each column equals the count of recap turns in exactly that range on 779 of 779 `all_01` rows. There is **no 20-based bucket for 180**: a 180 is in neither family's top 20-based band here — it is counted only in the `180` column — and turns below 100 are in none. Identities holding on all 3,313 01 rows that have the columns: `100+ = T00_19 + T20_39 + T40_59 + T60_79 + 180` and `140+ = T40_59 + T60_79 + 180`. The two families overlap (a 105 is in `T95_113` and `T00_19`), so never add a 19-based and a 20-based column together. |
| `Avg Fin` | Average finish (checkout) value. **[inferred]**; checked ≤ `HDO` on every row where both are present. |
| `CO Turn %` | **Checkout-turn percentage**: replay each leg's remaining score turn by turn; a busted turn counts as 0. **[verified]** only as the identity `CO Turn % = 100 × CO Darts / CO Opp` on all 3,291 rows where `CO Opp` > 0; the replay definition itself is **[inferred]** and was not recomputed from turns. |
| `CO Darts`, `CO Opp` | The numerator and denominator of `CO Turn %` (`CO Opp` = checkout-turn opportunities, `CO Darts` = those converted). **[inferred]** from the identity above. Observed: `CO Darts` ≤ `LWon` (1,340 of 1,340 rows checked) and ≤ `Legs`; `CO Opp` is *not* bounded by `Legs`, so it is not a per-leg count. |

**The "CO" (Check Out) columns that are mostly blank.** `CO Att`, `CO %` and `Tracked Legs` come from an
**opt-in, per-turn checkout prompt** that is active only for a subset of matches: it needs extra per-turn input from
the scorer that is usually not provided. So these columns are blank or zero for most players and most seasons, and
carry meaning only where that input was given. Treat a blank as "not tracked", never as zero. `CO %` is the one
checkout-percentage column; it is also referred to as "CO Dart %" — that is the same metric, not a separate (missing)
column.

| Column | Meaning |
|--------|---------|
| `Tracked Legs` | Number of the player's legs in which the checkout prompt was answered. **[inferred]**; consistent with the data: `Tracked Legs` ≤ `Legs` on every row, non-zero in only 167 of 2,631. |
| `CO Att` | Checkout attempts: raw single-dart attempts that could have resulted in a double-out (a game-ending dart), in tracked legs. **[inferred]**; populated in only 318 of 2,631 rows. |
| `CO %` | **Checkout percentage** — checkouts made divided by checkout attempts (`CO Att`), as a percentage with 2 decimals (the "CO Dart %" metric). **[verified]** as a ratio: on all 251 `singles_501` / `all_01` rows with `CO Att` > 0, `CO % × CO Att / 100` is a whole number, and that number is ≤ `Tracked Legs`, ≤ `CO Darts` and ≤ `LWon` on every one of the 251 — i.e. it behaves as a count of checkouts in the tracked legs. Blank when `CO Att` is blank or 0 (85 rows have `CO Att` = 0). **[inferred]** that the numerator is specifically "checkouts in tracked legs". It is **not** `100 × CO Darts / CO Att` (`CO Darts` counts checkouts in all legs, tracked or not), so the numerator is not a published column. |

### Cricket cuts (`singles_cricket`, `all_cricket`) — additional columns

| Column | Meaning |
|--------|---------|
| `Marks Scored` | Total marks. **[inferred]** |
| `MPR` | Marks per round. **[verified]**: `Marks Scored / (Darts Thrown / 3)` on all 3,326 rows. (A closing round can have fewer than 3 darts, so a per-round calculation from turn data can differ slightly.) |
| `O-MPR` | **Opponent MPR** (by analogy with `O-3DA`, which is verified). **[inferred]**; not recomputed. |
| `Miss%`, `T&B%` | Percentages — likely miss rate and triples-and-bulls rate. **[inferred]**, not checked. |
| `5M`, `6M`, `7M`, `8M`, `9M` | Counts of **rounds (turns)** with exactly 5, 6, 7, 8 marks, and **9** for `9M` (a turn of three darts can score at most 9 marks, so "9" and "9 or more" are the same). A turn's marks are the marks its darts scored on the cricket numbers 15–20 and bull (single = 1, double = 2, triple = 3; a single bull = 1, a double bull = 2). **[verified]**: each column equals the count of recap turns with that many marks on all 262 `all_cricket` rows tested (non-zero in 155, 69, 33, 3 and 4 rows respectively for `5M`…`9M`; `8M` and `9M` rest on few rows). |
| `5M+`, `7M+` | Rounds with 5-or-more / 7-or-more marks (DC's "5M+" / "7M+"). **[verified]** by checking: `5M+ = 5M+6M+7M+8M+9M` and `7M+ = 7M+8M+9M` on all 2,639 rows. |
| `3B`, `4B`, `5B`, `6B` | Counts of **rounds** with exactly 3, 4, 5 bull marks, and 6 for `6B` (a single bull is 1 mark, a double bull 2, so three darts can score at most 6 bull marks). **[verified]** for `3B`, `4B`, `5B`: each equals the count of recap turns with that many bull marks on all 262 `all_cricket` rows tested (non-zero in 63, 19 and 4 rows). `6B` matched on all 262 rows but was **zero in every one of them** (a 6-bull turn — three double bulls — is rare), so it is **[inferred]** by analogy with the others. |
| `HT` | **Hat tricks** — rounds where **all three darts hit the bull**. **[verified]**: equals the count of recap turns whose three darts were all bull (single or double) on all 262 `all_cricket` rows tested (non-zero in 22 of them). It is less than `3B` because a `3B` round (exactly 3 bull marks) can be earned with only **two** darts (a single bull + a double bull), whereas an `HT` needs all three darts on the bull. In the tested rows 3B counted 100 rounds: 80 were two-dart and 20 were three-dart rounds (those 20 are hat tricks), and `3B = (two-dart 3B rounds) + (three-dart 3B rounds)` held on every row. Relation: `HT ≤ 3B` on 3,328 of the 3,384 cricket-cut rows in the corpus (and `HT ≤ 3B + 4B + 5B + 6B` on all 3,384): the 56 exceptions are players whose hat tricks scored 4 or more bull marks (e.g. double bull + single + single = 4), which are counted in `4B`/`5B`/`6B` instead of `3B`. In the 262 tested rows, 4 hat-trick rounds scored 4+ bull marks. |

## `leaderboard_match_record.csv` (DC's `all` cut)

Header: `"Last","First",["Gender",]"Team","Division","Legs","Matches","Sets","Legs Win","Swon","STied","Match Wins","Match Ties","Leg Losses","LW%","Set Losses","Set Win%"`

| Column | Meaning |
|--------|---------|
| `Legs` | Legs played across all game types. **[inferred]**; equals `Legs` in `all_01` + `Legs` in `all_cricket` in 1,512 of the 1,523 rows that join (the others are name/record mismatches between cuts). |
| `Matches` | Matches played. **[inferred]** |
| `Sets` | Sets played. **[verified]** `Sets = Swon + STied + Set Losses` on all 1,692 rows. Not always equal to `Legs` (775 rows differ). |
| `Legs Win` | **Count** of legs won. **[verified]**: `Leg Losses = Legs − Legs Win`; `LW% = 100 × Legs Win / Legs`. |
| `Swon` | Sets won. **[verified]** (`Set Win% = 100 × Swon / Sets`) |
| `STied` | Sets tied. **[verified]** counted in `Sets`; see GOTCHAS #24 for how it affects `Set Win%`. Blank when zero. |
| `Match Wins`, `Match Ties` | **Blank in every row of the corpus** (0 populated of 1,692). Meaning never observed. **[unknown]** |
| `Leg Losses` | Legs lost. **[verified]** |
| `LW%` | Leg win % (2 decimals). **[verified]** |
| `Set Losses` | Sets lost. **[verified]** |
| `Set Win%` | Set win % = `Swon / Sets`; a tied set counts as **zero** (not half) — GOTCHAS #24. **[verified]** |

## `matchlog_reg.csv` / `matchlog_post.csv` (DC match log — published cell-for-cell; rows sorted chronologically — see README "Row order")

Header: `"Report","League ID","Day","Date","Source","Season","Division","Away/Guest @ Home/Host","Set Score","Legs Score","League Points","Start Time","End Time","Duration","DER","","Report Link","Event Link"`

| Column | Meaning |
|--------|---------|
| `Report` | Constant `Match Scores` in every row. **[verified]** |
| `League ID` | The league code (`ADDA` / `ADDACL`) — **not** a player id and unrelated to players.csv's removed `League Id`. **[verified]** |
| `Day`, `Date` | Weekday abbreviation and `m/d/yyyy` match date. **[verified]** |
| `Source` | `Scoring App` (scored live in DC, has a recap link) or `League Portal` (entered by hand / forfeit; no throw data). **[verified]** |
| `Season` | The **phase** — `REG` or `POST` — not a season. **[verified]** |
| `Division` | Division label. **Not normalized**: regular logs use `A`–`E`/`Coed`; post-season logs use labels like `Division A`, `Divisions B & C`, `ADDA Cup`, `Rob Spears Memorial Cup`, `PBR Cup`. **[verified]** |
| `Away/Guest @ Home/Host` | `Away team @ Home team`. **[verified]** |
| `Set Score`, `Legs Score`, `League Points` | `AA @ HH` zero-padded scores, away first. Set/leg score blank for `League Portal` rows. **[inferred]** |
| `Start Time`, `End Time` | 24-hour clock with **unpadded minutes** (`22:6` = 22:06) — GOTCHAS #20. **[verified]** |
| `Duration` | **Playing time of the match, in minutes.** **[verified]** — equals the match's `matchInfo.match_length` (`HH:MM`) on its recap page, within 1 minute of rounding, for 125 of 125 ADDA Spring 2026 matches checked (see `RECAPS.md`). It is *not* `End Time − Start Time` (equal in 1 of 1,308 rows that have all three) because it counts time on the game clocks, not wall-clock. |
| `DER` | Value equals the recap page's `matchInfo.der` (125 of 125 checked; values like `97`, `100`). **[verified]** as a pass-through; **[unknown]** what DC means by it (not defined by DC or ADDA's code). |
| *(empty header)* | Always blank. **[verified]** |
| `Report Link` | DC recap URL for the match (`recap.dartconnect.com/history/report/match/<id>`); blank for `League Portal` rows. Per-match/leg opponent detail lives behind this link (GOTCHAS #27). **[verified]** |
| `Event Link` | DC recap URL for an *event*; populated in only a couple of rows. **[inferred]** |

## ADDAs

*This section is ADDA's own public methodology, reproduced from the FAQ on the live page
[addadarts.com/season-stats](https://addadarts.com/season-stats) so the corpus is self-contained. The page is
authoritative if the two ever differ.*

**What ADDAs are.** "ADDAs" are ADDA's term for **high-scoring turns** in '01 and in cricket. Each turn earns 0–3 ADDAs:

| '01 turn score | ADDAs |
|---|---|
| 95–132 | 1 |
| 133–170 | 2 |
| 171–180 | 3 |

| Cricket marks in the turn | ADDAs |
|---|---|
| 5–6 marks | 1 |
| 7–8 marks | 2 |
| 9 marks | 3 |

| Cricket bulls in the turn | ADDAs |
|---|---|
| 3B (3 bull marks) | 1 |
| 4B or 5B | 2 |
| 6B | 3 |

**'01 ADDAs formula** (uses the 19-based buckets above):

```
'01 ADDAs = 95 + T14 + 2*(T33 + T52) + 3*T171
```

where `95` = `T95_113`, `T14` = `T14_32`, `T33` = `T33_51`, `T52` = `T52_70`, `T171` = `T71_80`. (`T95_113` and `T14_32`
together cover 95–132 and count once each; `T33_51` and `T52_70` cover 133–170 and count twice; `T71_80` covers
171–180 and counts three times.) The 20-based `T00_19`…`T60_79` columns are **not** used.

**Cricket ADDAs formula:**

```
Cricket ADDAs = 5M + 6M + 2*(7M + 8M) + 3*9M + 3B + 4B + 5B + 2*6B
```

**Why `6B` is multiplied by 2, not 3.** A 6-bull turn is worth 3 ADDAs, but DartConnect *also* credits that same
turn as a `6M` (a 6-mark round, worth 1 ADDA). The formula therefore counts the `6B` column as 2 so the `6M` supplies the
third ADDA and nothing is counted twice.

**Qualification.** For **501 3DA** and **cricket MPR**, a player must have played a singles set in **more than half**
of their team's matches to qualify.

**Shanghai (coed).** DC cannot track Shanghai ADDAs, so since the January 2025 coed meeting Shanghai ADDAs are
**excluded** from individual stats (GOTCHAS #23).

**Column cross-references from the FAQ** (they agree with the definitions above):

| Name used on the stats page | Column in these files |
|---|---|
| "High In" | `HDIT` |
| "High Out" | `HDO` |
| "Player Points" | `Swon` (sets won; in `leaderboard_match_record.csv`) |
| 501 Average | the first column in the Singles 501 table — `3DA` |
| Cricket MPR | the first column in the Singles Cricket table — `MPR` |

## `adda/` canonical files

ADDA's own layer (not DartConnect data; see the README). Every id column is first.

### `adda/players.csv` — canonical players

One row per `adda_player_id` (one per person, across both leagues and pre-DC history).

| Column | Meaning |
|--------|---------|
| `adda_player_id` | ADDA's canonical player id (the id addadarts.com uses). |
| `name` | The correct / current name for the person. Prefer it over any season-specific spelling. |
| `gender` | `M` / `F` / `U` / blank (blank = not recorded). Published for **every** player, in both leagues — this is the one place gender is published for ADDA players. A registration-style field, not a verified attribute. |

The file lists every player in ADDA's canonical records, including some who never appear in a DC season file
and the per-team `zz Alternate zz` placeholder records (GOTCHAS #5).

### `adda/teams.csv` — canonical teams

One row per `adda_team_id`.

| Column | Meaning |
|--------|---------|
| `adda_team_id` | ADDA's canonical team id. |
| `name` | The team's **current** name = its name in its most recent season. |
| `league` | `ADDA` or `ADDACL`. |
| `current_venue` | The team's venue **as of its latest season** (blank if none recorded). Teams move; this is not the venue for earlier seasons — use that season's `players.csv` `Venue`. Blank for older teams that never had a venue recorded (every team that appears in a DartConnect season file has one). |

### `adda/player_crosswalk.csv`, `adda/team_crosswalk.csv`

Per-(league, season) DC rows → canonical ids; columns are defined in [`adda/README.md`](adda/README.md).
