# Reading Dart Connect recap pages

The match logs (`matchlog_reg.csv`, `matchlog_post.csv`) carry a `Report Link` for every match scored live in
Dart Connect (DC). Those links are DC's **public recap pages**. The CSVs in this corpus are team-level; the
per-set, per-leg and per-turn detail ("who threw what against whom") exists only on the recap pages
(GOTCHAS #27). This guide describes how the pages are laid out and how to read them programmatically.

> **Status of this guide.** DC does not document these pages. Everything below was **observed** on
> ADDA/ADDACL recaps (2026 seasons) and is [verified] only in the sense "seen in real pages"; any of it can
> change without notice. Write your parser defensively (missing keys, `null`s, extra keys).

## Please be a good citizen

**These pages belong to Dart Connect.** They are served publicly, without a login, but that does not make
them ADDA's to license or yours to hammer. Before building anything that fetches them at scale, read
[DC's terms](https://www.dartconnect.com/league-administrator-updates/export-leaderboard/) and DC's site
terms, and ask DC if your use is beyond casual/hobby analysis. In practice:

- Fetch **only the matches you need**, and **cache what you fetch** — a recap for a finished match never changes
  (see "Stability" below), so never re-fetch it.
- **Go slowly and serially.** A request every few seconds is reasonable; do not parallelise. If you start
  seeing `429`/`5xx`, back off and stop.
- Identify your client with an honest `User-Agent` (ideally with a contact address).
- Do not republish bulk recap HTML/JSON without checking with DC; this corpus republishes only the CSV
  exports and the links.
- Everything here relies on **public, unauthenticated** pages only. Nothing in this guide needs a login,
  token or private endpoint, and you should not go looking for one.

## URL shape

Every recap is identified by a **24-character lowercase-hex match id**:

```
https://recap.dartconnect.com/history/report/match/<matchId>     <- the Report Link in the match logs
```

Extract the id with `/([a-f0-9]{24})$/` from `Report Link`. Rows with `Source = League Portal` (forfeits /
hand-entered results) have a blank `Report Link` and no recap (GOTCHAS #21). `Event Link` (two rows) points at
an *event* recap, which is a different page kind and is not covered here.

The recap site's own pages for the same match id that carry the data in a machine-readable form are:

| Page | Contains |
|------|----------|
| `https://recap.dartconnect.com/matches/<matchId>` | Match summary: team/match totals and, for every leg, **per-side** results (PPR or MPR, darts thrown, starting/ending points or marks, who won, which players). No individual turns. |
| `https://recap.dartconnect.com/games/<matchId>` | Everything above's leg list **plus every turn** of every leg (who threw, the turn score, the running score), per-leg duration, who won the leg and who threw first. |

(We have not confirmed that the `/history/report/match/<id>` link serves the same payload as `/matches/<id>`
— use the two pages above, which we have read successfully, and treat the link as a human-readable page.)

## How the page carries its data

Both pages are a server-rendered single-page app (Inertia.js). The HTML contains one element whose
`data-page` attribute is **the page's whole data payload as HTML-escaped JSON**:

```html
<div id="app" data-page="{&quot;component&quot;:&quot;Games/Show&quot;,&quot;props&quot;:{ ... }}">
```

So you do not need to scrape visible markup: fetch the HTML, pull out `data-page`, unescape, `json.loads`.

```python
import html, json, re, urllib.request

def fetch_recap(match_id: str, kind: str = "games") -> dict:          # kind: "games" | "matches"
    req = urllib.request.Request(
        f"https://recap.dartconnect.com/{kind}/{match_id}",
        headers={"User-Agent": "my-league-analysis/0.1 (you@example.com)"},   # be honest about who you are
    )
    raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    m = re.search(r'data-page="([^"]+)"', raw)
    if not m:
        raise ValueError("no data-page attribute - page layout changed, or not a recap page")
    return json.loads(html.unescape(m.group(1)))["props"]              # the payload you want lives in "props"
```

The payload also carries framework plumbing (a route table, auth stubs, asset versions). **Ignore it** — the
data you want is under `props.matchInfo` and `props.segments` only (plus `props.homePlayers` / `awayPlayers`
on `/matches/`).

## `props.matchInfo` — the match header

Observed keys that are useful (values are mostly **strings**, including numbers with thousands separators like
`"11,106"` — strip commas before converting):

| Key | Meaning |
|-----|---------|
| `id` | The 24-hex match id (same as the URL). |
| `home_label`, `away_label` | Team names. **Home/away here matches the match log's `Away @ Home` order.** |
| `league_id`, `event_title`, `division_title` | e.g. `ADDA`, `Spring 2026`, `Division: B`. |
| `server_match_start_date` | e.g. `Mon, 26-Jan-2026`. |
| `match_start_date`, `match_end_date` | Clock times, 12-hour (`7:55 PM`). Correspond to the log's `Start Time` / `End Time`. |
| `match_length` (and `game_time`) | `HH:MM` of **playing time**. **[verified]** The match log's `Duration` column is this value **in minutes** (ADDA Spring 2026, 125 of 125 matches checked: equal, or 1 minute higher from rounding). It is *not* end − start. |
| `der` | A number such as `100`. **[verified]** identical to the match log's `DER` column (same 125 of 125). Its meaning is not documented by DC. |
| `opponents[]` | Two objects (one per side): `name`, `set_wins`, `leg_wins`, `league_points`, `ppr`, `mpr`, `darts_thrown_ppr`, `darts_thrown_mpr`, `points_scored_ppr`, `marks_scored`. |
| `match_winner` | `0` or `1`, index into `opponents`. |
| `total_sets`, `total_games`, `total_01_darts_thrown`, `total_cricket_darts_thrown`, `total_marks_scored`, `total_points_scored` | Whole-match totals (strings). |
| `notes` | Free-text notes DC attached to the match/sets (usually empty). |

## `props.segments` — sets and legs

`segments` is a dictionary keyed by the **segment number as a string**. A segment is one game slot of the match
format, e.g. for ADDA Monday league:

| Key | `league_segment.label` | `game_name` seen |
|-----|------------------------|------------------|
| `"1"` | Singles 501 | `501` (on `/games/`: `501 SIDO`) |
| `"2"` | Singles Cricket | `Cricket` |
| `"3"` | Doubles 301 | `301` (`301 DIDO`) |
| `"4"` | Doubles Cricket | `Cricket` |
| `"5"` | Team 801 | `801` (`801 SIDO`) |

Other leagues/formats (e.g. ADDACL) use different segment layouts — **key on `league_segment.label`, not on the
number.** `SIDO` / `DIDO` = straight-in / double-in, double-out.

**Nesting:** `segments[segment]` is a list of **sets** (in play order); each set is a list of **legs**
(1 leg for a single-leg set, up to 3 for best-of-3). So `segments["1"][0][0]` is the first leg of the first
set of Singles 501. The set's winner is the side that won more of its legs.

Per-leg keys (both pages): `league_segment{label, segment_number, set_id, segment_id}`, `game_name`,
`score_type` (`"P"` = points/01, `"M"` = marks/cricket), `darts_thrown`, `is_forfeit`, `score_edits`
(manual corrections to the score, if any), and two side objects, **`home`** and **`away`**:

| Side key | Meaning |
|----------|---------|
| `ppr` / `mpr` | Points (01) or marks (cricket) per round for that side in the leg — strings. |
| `starting_points` → `ending_points` | 01 legs: the start score and what the side had left (`0` = finished). `/matches/` only. |
| `double_out_points` | 01 legs: the finishing turn's score when the side checked out. `/matches/` only. |
| `ending_marks` | Cricket legs: total marks. |
| `players[]` | `/matches/`: the players on that side for this leg, `{player_label: "First Last"}` (labels are `First Last`; the roster CSV splits them). |
| `win` | `true` for the side that won the leg. `/matches/` only. |

Differences between the two pages you will trip over: on `/games/` the leg winner is `winner_index`
(`0` = home, `1` = away) and the thrower order is `starting_opponent_index`, the per-leg clock is `duration`
(`MM:SS`), and leg/set counters are named `set_game_number` / `set_index` (and are not numbered the same way
as on `/matches/`, where they are `set_number` / `set_index` with `set_index` starting at 0). Number legs by
**list position**, not by those fields. `darts_thrown` is often present only for the side that finished the leg.

## `turns[]` — per-turn detail (`/games/` only)

Each leg on `/games/` has `turns`, a list in throw order; each element has a `home` and an `away` object:

| Key | Meaning |
|-----|---------|
| `name` | Player who threw that turn (`First Last`). **This is how you attribute doubles turns to a partner.** |
| `turn_score` | 01: integer points scored that turn. Cricket: a **string describing the darts** (e.g. `S20`, `S20x2`) — the format is undocumented; parse with care. |
| `current_score` | 01: the side's remaining score after the turn. |
| `notable`, `color` | Highlights DC flags, e.g. `notable: 121, color: "TON 21"` for 121, `notable: "100", color: "TON"`. |
| `opponent_index`, `is_starting_opponent` | Which side this is / who threw first. |

Turns alternate between the sides, so `home` and `away` entries are side by side in each element.

## Worked example — every 01 turn of a match, per player

```python
props = fetch_recap("69780e4f0efa95bbe4986c57", "games")
for seg in props["segments"].values():
    for set_no, legs in enumerate(seg, 1):
        for leg_no, leg in enumerate(legs, 1):
            if leg["score_type"] != "P":
                continue                                   # skip cricket legs (string turn_scores)
            for t in leg["turns"]:
                for side in ("home", "away"):
                    s = t.get(side) or {}
                    if isinstance(s.get("turn_score"), int):
                        print(leg["league_segment"]["label"], set_no, leg_no, side, s["name"], s["turn_score"])
```

## Stability and cautions

- **Finished matches don't change**, but a match can be corrected afterwards (`score_edits`). Re-check a
  recent match once before treating it as final.
- Turn data exists only for matches **scored live in the DC scoring app**. `League Portal` rows have none.
- The payload also contains per-player account flags (membership, e-mail status). They are not part of this
  corpus and there is no reason to collect or redistribute them.
- Player names on recaps are DC's display labels; to tie them to ADDA ids use `adda/player_crosswalk.csv` (join through
  the roster `ID`/team/season), and expect name variants (GOTCHAS #25).
- Recap-derived figures will not always equal the leaderboard CSVs: the leaderboards are DC's own rollups (and
  Doubles Shanghai is not scorable in DC at all — GOTCHAS #23).

## Not covered here

This guide deliberately covers only reading DC's public pages. It does not describe any ADDA-internal storage,
scheduling, caching, or downstream stats pipeline.
