"""Check that the docs still match the published data, and carry no internal references.

Run from the repo root: python3 .github/scripts/check_docs.py
Exits non-zero (listing every problem) if any check fails. Standard library only.

The data files (manifest.json, dartconnect/, adda/*.csv) are pushed by the nightly publish job; the docs are
edited here by hand. This catches the two drifting apart in either direction: a doc PR that drops or renames a
documented column, or a data push that brings a column, removed column or deviation the docs don't describe. Where
the docs give a file's exact header, the files must match it exactly (names and order).
"""

import collections
import csv
import glob
import json
import os
import re
import sys

problems = []


def fail(msg):
    problems.append(msg)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def code_spans(md):
    """Every `code span` (spans may wrap lines), outside fenced blocks."""
    md = re.sub(r"^```.*?^```", "", md, flags=re.S | re.M)  # fenced blocks would throw off the backtick pairing
    return re.findall(r"`([^`]+)`", md)


def code_names(md):
    """Every name written in a `code span` (comma-separated lists are split)."""
    return {" ".join(part.split()) for span in code_spans(md) for part in span.split(",")}


def describe_mismatch(doc_cols, file_cols):
    missing = [c for c in doc_cols if c not in file_cols]
    extra = [c for c in file_cols if c not in doc_cols]
    if not missing and not extra:
        return "same columns, different order"
    return "; ".join(s for s in (f"documented but not in the file: {missing}" if missing else "",
                                 f"in the file but not documented: {extra}" if extra else "") if s)


def header(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f), [])


readme, columns_md, adda_md = read("README.md"), read("COLUMNS.md"), read("adda/README.md")
manifest = json.loads(read("manifest.json"))

# 1. Every published column is documented: dartconnect/ columns in COLUMNS.md, adda/ columns in adda/README.md.
#    DC's match logs have one column with an empty header; COLUMNS.md documents it as "(empty header)".
documented = code_names(columns_md)
for path in sorted(glob.glob("dartconnect/**/*.csv", recursive=True)):
    for col in header(path):
        if col == "" and "(empty header)" in columns_md:
            continue
        if col not in documented:
            fail(f"{path}: column {col!r} is not documented in COLUMNS.md")
documented_adda = code_names(adda_md)
for path in sorted(glob.glob("adda/*.csv")):
    for col in header(path):
        if col not in documented_adda:
            fail(f"{path}: column {col!r} is not documented in adda/README.md")

# 1b. Documented exact headers match the files (names and order).
#   COLUMNS.md: a "Header: `...`" or "Header as published: `...`" line applies to every dartconnect/ file named
#   (by .csv name) in its section heading. Mismatches are grouped, so one stale line is one problem, not 50.
dc_files = sorted(glob.glob("dartconnect/**/*.csv", recursive=True))
heading_files = []
for line in columns_md.splitlines():
    if line.startswith("#"):
        heading_files = [n.rsplit("/", 1)[-1] for n in re.findall(r"`([^`]+\.csv)`", line)]
        continue
    m = re.match(r"^Header(?: as published)?: `(.+)`\s*$", line)
    if not m:
        continue
    doc_cols = next(csv.reader([m.group(1)]))
    files = [p for p in dc_files if os.path.basename(p) in heading_files]
    if not files:
        fail(f"COLUMNS.md: header line under a heading naming {heading_files or 'no .csv file'} matches no published file")
        continue
    bad = collections.defaultdict(list)
    for p in files:
        if header(p) != doc_cols:
            bad[tuple(header(p))].append(p)
    for file_cols, ps in bad.items():
        fail(f"COLUMNS.md: documented header for {'/'.join(heading_files)} differs from {len(ps)} of {len(files)} files "
             f"(e.g. {ps[0]}): {describe_mismatch(doc_cols, list(file_cols))}")

#   adda/README.md: a comma-separated `code span` list starting with an adda_*_id column is a documented header; it must
#   equal a published adda/ file's header. Every adda/ file must be documented either by such a list or by the column
#   order of its "## `<file>` columns" table.
adda_headers = {os.path.basename(p): header(p) for p in sorted(glob.glob("adda/*.csv"))}
doc_lists = []
for span in code_spans(adda_md):
    parts = [re.sub(r"\s*\(.*\)$", "", " ".join(p.split())) for p in span.split(",")]  # "match_method (name | ...)" -> name
    if len(parts) >= 3 and re.fullmatch(r"adda_\w+_id", parts[0]):
        doc_lists.append(parts)
        if parts not in adda_headers.values():
            closest = max(adda_headers.items(), key=lambda kv: (kv[1][0] == parts[0], len(set(kv[1]) & set(parts)) - len(set(kv[1]) ^ set(parts))))
            fail(f"adda/README.md: column list `{', '.join(parts)}` matches no adda/ file header "
                 f"(closest {closest[0]}: {describe_mismatch(parts, closest[1])})")
for name, cols in adda_headers.items():
    if cols in doc_lists:
        continue
    table = re.search(rf"^##+ `{re.escape(name)}` columns\s*$(.*?)(?=^#|\Z)", adda_md, re.S | re.M)
    if not table:
        fail(f"adda/{name}: header is not documented in adda/README.md (no column list, no '## `{name}` columns' table)")
        continue
    order = [" ".join(n.split()) for row in re.findall(r"^\|\s*(`[^|]+)\|", table.group(1), re.M)
             for span in re.findall(r"`([^`]+)`", row) for n in span.split(",")]
    if order != cols:
        fail(f"adda/README.md: '{name} columns' table differs from adda/{name}: {describe_mismatch(order, cols)}")

# 2. Every removed column (manifest columns_removed) is named in the README or COLUMNS.md.
documented_any = code_names(readme) | documented
for col in sorted({c for f in manifest["files"] for c in f.get("columns_removed", [])}):
    if col not in documented_any:
        fail(f"manifest.json: removed column {col!r} is not mentioned in README.md or COLUMNS.md")

# 3. The README's deviations table has one row per manifest deviation.
section = re.search(r"^## The \w+ deviations.*?$(.*?)^#", readme, re.S | re.M)
if not section:
    fail("README.md: no '## The ... deviations' section")
else:
    rows = re.findall(r"^\|\s*\d+\s*\|", section.group(1), re.M)
    if len(rows) != len(manifest["deviations"]):
        fail(f"README.md: deviations table has {len(rows)} rows, manifest.json lists {len(manifest['deviations'])} deviations")

# 4. No internal references (pipeline script names or the pipeline repo's name) in any .md / .yml file.
internal = re.compile(r"\.mjs\b|adda-data-" + "pipeline")
for path in sorted(set(glob.glob("**/*.md", recursive=True) + glob.glob("**/*.y*ml", recursive=True)
                       + glob.glob(".github/**/*.md", recursive=True) + glob.glob(".github/**/*.y*ml", recursive=True))):
    for n, line in enumerate(read(path).splitlines(), 1):
        if internal.search(line):
            fail(f"{path}:{n}: internal reference: {line.strip()[:120]}")

# 5. Issues stay the public forum: the README section and the issue templates exist.
if not re.search(r"^## Questions & Discussion", readme, re.M):
    fail("README.md: missing the '## Questions & Discussion' section")
templates = [p for p in glob.glob(".github/ISSUE_TEMPLATE/*") if not p.endswith("config.yml")]
if len(templates) < 1 or not glob.glob(".github/ISSUE_TEMPLATE/config.yml"):
    fail(".github/ISSUE_TEMPLATE: expected issue templates and a config.yml")

if problems:
    print(f"{len(problems)} problem(s):")
    for p in problems:
        print(f"  - {p}")
    sys.exit(1)
print("docs check: ok")
