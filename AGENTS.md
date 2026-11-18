# AGENTS.md

Instructions for AI agents and automated tools working with this repository.

## What this is

Open league data for the Atlanta-Decatur Dart Association: **ADDA** (Monday league) and **ADDACL** (Coed league).

- `dartconnect/{adda,addacl}/{season_num}/` — Dart Connect (DC) CSV exports, one folder per league and season. These are real
  DC exports, republished as-is except for the five published deviations (below). Nothing is synthesized or invented.
- `adda/` — ADDA's own canonical layer: one row per player and per team, plus crosswalks from each DC season row to those ids.
- `manifest.json` — lists every file with league, season, cut, date range, row counts, checksums and what was removed.
  `as_of` and each file's `archived_at` say what a given build reflects.

## Read these first

1. [`README.md`](README.md) — layout, the five deviations, row order, IDs, freshness, citation, license/terms.
2. [`GOTCHAS.md`](GOTCHAS.md) — read **before** computing or aggregating anything.
3. [`COLUMNS.md`](COLUMNS.md) — what each published column means.
4. [`RECAPS.md`](RECAPS.md) — how to read the per-match recap pages the match logs link to (per-leg / per-turn detail).
5. [`adda/README.md`](adda/README.md) — the canonical layer and crosswalks.

Start from `manifest.json` to discover files rather than guessing paths. Do not restate these docs from memory; read them.

## Identity and joins

`adda_player_id` and `adda_team_id` (in `adda/`) are the canonical cross-league keys and the only link to addadarts.com
(`https://addadarts.com/player-cards?id=…`, `https://addadarts.com/team-cards?id=…`). DC's `ID` is a per-league key, used to
join `players.csv` to the crosswalk. Use only crosswalk rows with `status = resolved` when linking. Details: README "IDs, and how
to link a row to addadarts.com" and GOTCHAS "Identity".

## Deviations from Dart Connect's files

Five deviations (contact info, `Country`, inactive rows, `League Id`, `League Status`/`Season Status`) are listed in README
("The five deviations from Dart Connect's files") and `manifest.json` → `deviations`; GOTCHAS covers their consequences.
Rows are also published in a deterministic sort (order only). Do not assume a column or row that is absent was never in DC's export.

## Currency and terms

There is no update guarantee beyond what the README's "Freshness" section says. Check the manifest's `as_of`; `in_progress`
seasons are partial and will change. `dartconnect/` is Dart Connect's data (no ADDA license); `adda/` and the docs are CC BY 4.0.
See README "License / terms" and "How to cite".

## Questions and data problems

Open an Issue on this repository (see README "Questions & Discussion"). Do not include private contact details.
