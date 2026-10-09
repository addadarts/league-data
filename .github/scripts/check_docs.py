"""Check that the docs still match the published data, and carry no internal references.

Run from the repo root: python3 .github/scripts/check_docs.py
Exits non-zero (listing every problem) if any check fails. Standard library only.

The data files (manifest.json, dartconnect/, adda/*.csv) are pushed by the nightly publish job; the docs are
edited here by hand. This catches the two drifting apart in either direction: a doc PR that drops or renames a
documented column, or a data push that brings a column, removed column or deviation the docs don't describe.
"""

import csv
import glob
import json
import re
import sys

problems = []


def fail(msg):
    problems.append(msg)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def code_names(md):
    """Every name written in a `code span` (spans may wrap lines; comma-separated lists are split)."""
    names = set()
    md = re.sub(r"^```.*?^```", "", md, flags=re.S | re.M)  # fenced blocks would throw off the backtick pairing
    for span in re.findall(r"`([^`]+)`", md):
        for part in span.split(","):
            names.add(" ".join(part.split()))
    return names


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
