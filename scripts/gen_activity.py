#!/usr/bin/env python3
"""Render the contribution heatmap as a self-contained SVG (dark + light).

Pulls the real calendar from the GitHub GraphQL API so the README never depends
on a third-party chart service. Re-run to refresh.
"""

import json
import os
import subprocess
from datetime import date, timedelta

LOGIN = os.environ.get("GH_LOGIN", "MUHAMMEDHAFEEZ")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

MONO = "ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace"

THEMES = {
    "dark": {
        "panel": "#11161F", "line": "#242C3A", "text": "#E6EDF3",
        "dim": "#7D8590", "accent": "#D8A657",
        "ramp": ["#1A202B", "#4A3A1E", "#8A6B2E", "#C09242", "#D8A657"],
    },
    "light": {
        "panel": "#F7F9FC", "line": "#D6DEE8", "text": "#141A22",
        "dim": "#5A6474", "accent": "#9A6700",
        "ramp": ["#E9EDF3", "#F0DFB0", "#DFC077", "#BF9A3F", "#9A6700"],
    },
}

QUERY = """
query($login:String!){
  user(login:$login){
    contributionsCollection{
      contributionCalendar{
        totalContributions
        weeks{ contributionDays{ date contributionCount weekday } }
      }
    }
  }
}
"""


def fetch(login):
    raw = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"login={login}"],
        capture_output=True, text=True, check=True,
    ).stdout
    return json.loads(raw)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def streaks(days):
    """days: list of (date, count) in chronological order."""
    longest = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)

    # current streak counts back from today (a still-empty today doesn't break it)
    by_date = dict(days)
    cur, cursor = 0, date.today()
    if by_date.get(cursor, 0) == 0:
        cursor -= timedelta(days=1)
    while by_date.get(cursor, 0) > 0:
        cur += 1
        cursor -= timedelta(days=1)
    return cur, longest


def levels(counts):
    """Four ascending thresholds from the non-zero distribution."""
    nz = sorted(c for c in counts if c > 0)
    if not nz:
        return [1, 2, 3, 4]
    return [max(1, nz[int(len(nz) * q)]) for q in (0.25, 0.50, 0.75, 0.90)]


def level_of(count, th):
    if count <= 0:
        return 0
    for i, t in enumerate(th):
        if count <= t:
            return i + 1
    return 4


def build(cal, c):
    W, CELL, GAP = 880, 11, 3
    PITCH = CELL + GAP
    weeks = cal["weeks"]
    grid_x, grid_y = 70, 78
    grid_h = 7 * PITCH - GAP
    bottom = grid_y + grid_h + 30
    H = bottom + 22

    days = [(d["date"], d["contributionCount"])
            for w in weeks for d in w["contributionDays"]]
    counts = [n for _, n in days]
    th = levels(counts)
    total = cal["totalContributions"]
    active = sum(1 for n in counts if n > 0)
    busiest = max(counts)

    p = []
    add = p.append
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{total} contributions in the last year">')
    add(f"<style>.m{{font-family:{MONO}}}</style>")
    add(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" '
        f'fill="{c["panel"]}" stroke="{c["line"]}"/>')

    # header strip
    add(f'<text class="m" x="40" y="38" font-size="10.5" letter-spacing="1.6" '
        f'fill="{c["accent"]}">LAST 12 MONTHS</text>')
    add(f'<text class="m" x="840" y="38" font-size="10.5" letter-spacing="1.6" text-anchor="end" '
        f'fill="{c["text"]}">{total:,} CONTRIBUTIONS</text>')

    # month labels
    prev = None
    for wi, w in enumerate(weeks):
        d = date.fromisoformat(w["contributionDays"][0]["date"])
        if d.month != prev and wi < len(weeks) - 1:
            add(f'<text class="m" x="{grid_x + wi*PITCH}" y="{grid_y - 9}" font-size="9" '
                f'fill="{c["dim"]}">{d.strftime("%b")}</text>')
            prev = d.month

    # weekday labels
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        add(f'<text class="m" x="{grid_x - 9}" y="{grid_y + row*PITCH + 8.5}" font-size="9" '
            f'text-anchor="end" fill="{c["dim"]}">{label}</text>')

    # grid
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            x = grid_x + wi * PITCH
            y = grid_y + d["weekday"] * PITCH
            fill = c["ramp"][level_of(d["contributionCount"], th)]
            add(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{fill}"/>')

    # legend + streaks
    add(f'<text class="m" x="40" y="{bottom + 8}" font-size="9" fill="{c["dim"]}">LESS</text>')
    for i, col in enumerate(c["ramp"]):
        add(f'<rect x="{76 + i*PITCH}" y="{bottom}" width="{CELL}" height="{CELL}" rx="2" fill="{col}"/>')
    add(f'<text class="m" x="{76 + 5*PITCH + 4}" y="{bottom + 8}" font-size="9" fill="{c["dim"]}">MORE</text>')
    add(f'<text class="m" x="840" y="{bottom + 8}" font-size="9.5" letter-spacing="1.2" text-anchor="end" '
        f'fill="{c["dim"]}">ACTIVE DAYS '
        f'<tspan fill="{c["text"]}">{active}</tspan>  &#183;  BUSIEST DAY '
        f'<tspan fill="{c["text"]}">{busiest}</tspan></text>')

    add("</svg>")
    return "\n".join(p), (total, active, busiest)


def main():
    cal = fetch(LOGIN)
    os.makedirs(OUT, exist_ok=True)
    stats = None
    for theme, c in THEMES.items():
        svg, stats = build(cal, c)
        path = os.path.join(OUT, f"activity-{theme}.svg")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(f"wrote {path} ({os.path.getsize(path)} bytes)")
    print(f"total={stats[0]:,}  active_days={stats[1]}  busiest={stats[2]}")


if __name__ == "__main__":
    main()
