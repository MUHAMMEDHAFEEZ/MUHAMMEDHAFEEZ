#!/usr/bin/env python3
"""Generate the README SVG assets (dark + light) for the profile repo.

Design: "service status page" — the profile presented as a backend service.
Everything is self-contained SVG so the README never depends on a third-party
badge service that can go down.
"""

import os
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

THEMES = {
    "dark": {
        "ground": "#0D1117",
        "panel":  "#11161F",
        "line":   "#242C3A",
        "text":   "#E6EDF3",
        "dim":    "#7D8590",
        "live":   "#3FB950",
        "accent": "#D8A657",
        "data":   "#58A6FF",
        "grid":   "#FFFFFF",
    },
    "light": {
        "ground": "#FFFFFF",
        "panel":  "#F7F9FC",
        "line":   "#D6DEE8",
        "text":   "#141A22",
        "dim":    "#5A6474",
        "live":   "#1A7F37",
        "accent": "#9A6700",
        "data":   "#0969DA",
        "grid":   "#000000",
    },
}

MONO = "ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace"
SANS = "ui-sans-serif,-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif"

# monospace advance width is ~0.6em
def mono_w(text, size, tracking=0.0):
    return len(text) * (size * 0.6 + tracking)


# --------------------------------------------------------------------------
# Header banner
# --------------------------------------------------------------------------
def header(c):
    W, H = 880, 190

    # request-flow nodes: (x, width, label, emphasised)
    nodes = [(588, 62, "CLIENT", False), (690, 62, "API", True), (792, 48, "DB", False)]
    node_y, node_h = 76, 40

    parts = []
    add = parts.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="Mohammed Hafeez — Backend Developer, Cairo Egypt">')

    add("<defs>")
    add(f'<pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="1" cy="1" r="1" fill="{c["grid"]}" opacity="0.05"/></pattern>')
    add('<clipPath id="card"><rect x="0" y="0" width="%d" height="%d" rx="14"/></clipPath>' % (W, H))
    add("</defs>")

    add("<style>"
        ".mono{font-family:%s}"
        ".sans{font-family:%s}"
        "@keyframes beat{0%%,100%%{opacity:1}50%%{opacity:.3}}"
        "@keyframes flow{0%%{transform:translateX(0);opacity:0}"
        "8%%{opacity:1}92%%{opacity:1}100%%{transform:translateX(232px);opacity:0}}"
        "@media (prefers-reduced-motion:no-preference){"
        ".beat{animation:beat 2.4s ease-in-out infinite}"
        ".packet{animation:flow 3.4s cubic-bezier(.45,.05,.55,.95) infinite}}"
        "</style>" % (MONO, SANS))

    # card
    add(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>')
    add(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#grid)" clip-path="url(#card)"/>')

    # ---- identity block -------------------------------------------------
    add(f'<circle class="beat" cx="48" cy="46" r="4.5" fill="{c["live"]}"/>')
    add(f'<text class="mono" x="64" y="50" font-size="11" letter-spacing="1.6" fill="{c["live"]}">ONLINE</text>')
    add(f'<text class="mono" x="132" y="50" font-size="11" letter-spacing="1.6" fill="{c["dim"]}">CAIRO, EG &#183; UTC+2</text>')

    add(f'<text class="sans" x="44" y="100" font-size="38" font-weight="700" letter-spacing="-0.8" '
        f'fill="{c["text"]}">Mohammed Hafeez</text>')
    add(f'<rect x="44" y="117" width="56" height="2" rx="1" fill="{c["accent"]}"/>')
    add(f'<text class="mono" x="44" y="142" font-size="13" fill="{c["dim"]}">'
        f'Backend Developer &#8212; APIs, async services &amp; developer tooling</text>')
    add(f'<text class="mono" x="44" y="167" font-size="10.5" letter-spacing="1.8" fill="{c["accent"]}">'
        f'PYTHON &#183; DJANGO &#183; DRF &#183; POSTGRESQL &#183; DOCKER</text>')

    # ---- request flow ---------------------------------------------------
    for x, w, label, strong in nodes:
        stroke = c["accent"] if strong else c["line"]
        add(f'<rect x="{x}" y="{node_y}" width="{w}" height="{node_h}" rx="8" '
            f'fill="{c["ground"]}" stroke="{stroke}"/>')
        add(f'<text class="mono" x="{x + w/2}" y="{node_y + node_h/2 + 3.5}" font-size="10" '
            f'letter-spacing="1.1" text-anchor="middle" '
            f'fill="{c["accent"] if strong else c["dim"]}">{label}</text>')

    cy = node_y + node_h / 2
    for x1, x2 in ((650, 690), (752, 792)):
        add(f'<line x1="{x1}" y1="{cy}" x2="{x2-6}" y2="{cy}" stroke="{c["line"]}" stroke-width="1.5"/>')
        add(f'<path d="M{x2-6} {cy-3.5} L{x2} {cy} L{x2-6} {cy+3.5} Z" fill="{c["line"]}"/>')

    add(f'<circle class="packet" cx="600" cy="{cy}" r="3.5" fill="{c["data"]}"/>')
    add(f'<text class="mono" x="714" y="140" font-size="9.5" letter-spacing="1.4" text-anchor="middle" '
        f'fill="{c["dim"]}">REQUEST FLOW</text>')

    add("</svg>")
    return "\n".join(parts)


# --------------------------------------------------------------------------
# Tech stack panel
# --------------------------------------------------------------------------
GROUPS = [
    ("LANGUAGES",     [("Python", 1), ("Java", 0), ("SQL", 0), ("C++", 0)]),
    ("FRAMEWORKS",    [("Django", 1), ("DRF", 1), ("Celery", 0), ("Flutter", 0), ("Spring Boot", 2)]),
    ("DATA",          [("PostgreSQL", 1), ("Redis", 0), ("MySQL", 0), ("SQLite", 0), ("Firebase", 0)]),
    ("INFRA & TOOLS", [("Docker", 1), ("AWS", 0), ("Git", 0), ("Postman", 0), ("Linux", 0)]),
]
# weight: 0 = familiar, 1 = core, 2 = currently learning


def stack(c):
    W = 880
    row_h, chip_h, gap = 60, 34, 10
    top = 24
    H = top + row_h * len(GROUPS) - (row_h - chip_h) + 24

    parts = []
    add = parts.append

    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="Tech stack">')
    add(f"<style>.mono{{font-family:{MONO}}}</style>")
    add(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" fill="{c["panel"]}" stroke="{c["line"]}"/>')

    # structural hairline between the label gutter and the chips
    add(f'<line x1="152" y1="{top - 4}" x2="152" y2="{H - top + 4}" stroke="{c["line"]}"/>')

    for i, (label, items) in enumerate(GROUPS):
        y = top + i * row_h
        add(f'<text class="mono" x="28" y="{y + 22}" font-size="10.5" letter-spacing="1.6" '
            f'fill="{c["accent"]}">{escape(label)}</text>')

        x = 172
        for name, weight in items:
            w = round(mono_w(name, 12) + 26)
            if weight == 2:                      # currently learning
                stroke, dash, fill = c["accent"], ' stroke-dasharray="4 3"', c["accent"]
            elif weight == 1:                    # core
                stroke, dash, fill = c["data"], "", c["text"]
            else:
                stroke, dash, fill = c["line"], "", c["dim"]
            add(f'<rect x="{x}" y="{y}" width="{w}" height="{chip_h}" rx="8" '
                f'fill="{c["ground"]}" stroke="{stroke}"{dash}/>')
            add(f'<text class="mono" x="{x + w/2}" y="{y + 22}" font-size="12" text-anchor="middle" '
                f'fill="{fill}">{escape(name)}</text>')
            x += w + gap

    add("</svg>")
    return "\n".join(parts)


def main():
    os.makedirs(OUT, exist_ok=True)
    for theme, c in THEMES.items():
        for name, builder in (("header", header), ("stack", stack)):
            path = os.path.join(OUT, f"{name}-{theme}.svg")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(builder(c))
            print(f"wrote {path}  ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
