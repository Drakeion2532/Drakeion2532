"""Builds every SVG on the profile README.

Static parts come from data/projects.json. Live parts (repo count, language
mix, last activity) come from the GitHub API when GITHUB_TOKEN is set (the
scheduled Action does this); otherwise data/github_cache.json is used.

    python scripts/build_profile.py
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import random
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USER = "Drakeion2532"

BG, PANEL, LINE = "#0B0B0E", "#141419", "#26262E"
TEXT, MUTED, DIM = "#F4F1EE", "#A29C98", "#6E6863"
EMBER, AMBER = "#FF5A1F", "#FFB23E"
SANS = "'Segoe UI', Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "'JetBrains Mono', 'Cascadia Code', Consolas, 'Courier New', monospace"
LANG_COLORS = {"Python": "#FF5A1F", "JavaScript": "#FFB23E", "Kotlin": "#C084FC", "C": "#5BC0EB",
               "C++": "#4ADE80", "CSS": "#F7D154", "HTML": "#FF8A65", "TypeScript": "#60A5FA",
               "Swift": "#FB7185", "Other": "#57534E"}


def esc(s) -> str:
    return escape(str(s), quote=True)


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{esc(title)}"><title>{esc(title)}</title>{body}</svg>\n')


def defs(extra=""):
    return (f'<defs><linearGradient id="ember" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{EMBER}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>'
            f'<linearGradient id="emberv" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{AMBER}"/><stop offset="1" stop-color="{EMBER}"/></linearGradient>'
            f'<radialGradient id="glow" cx="0.85" cy="0.35" r="0.6"><stop offset="0" stop-color="{EMBER}" stop-opacity="0.35"/>'
            f'<stop offset="1" stop-color="{EMBER}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="soft" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{EMBER}" stop-opacity="0.16"/>'
            f'<stop offset="1" stop-color="{EMBER}" stop-opacity="0"/></radialGradient>'
            f'<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">'
            f'<path d="M32 0H0V32" fill="none" stroke="#FFFFFF" stroke-opacity="0.035"/></pattern>{extra}</defs>')


def t(x, y, s, size=13, fill=TEXT, weight=400, anchor="start", font=SANS, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{font}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{extra}>{esc(s)}</text>')


# ----------------------------------------------------------------------------- circle primitives
def ring(cx, cy, r, frac, color, width=10, track=LINE, dashed=False, delay=0.0):
    """Progress ring that sweeps in from 12 o'clock."""
    c = 2 * math.pi * r
    arc = max(0.0, min(1.0, frac)) * c
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track}" stroke-width="{width}"/>'
    if dashed:
        return out + (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{width}" '
                      f'stroke-dasharray="6 7" opacity="0.8"><animateTransform attributeName="transform" type="rotate" '
                      f'from="0 {cx} {cy}" to="360 {cx} {cy}" dur="18s" repeatCount="indefinite"/></circle>')
    return out + (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{width}" '
                  f'stroke-linecap="round" stroke-dasharray="{arc:.2f} {c:.2f}" transform="rotate(-90 {cx} {cy})">'
                  f'<animate attributeName="stroke-dasharray" from="0 {c:.2f}" to="{arc:.2f} {c:.2f}" dur="1.4s" '
                  f'begin="{delay}s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1" keyTimes="0;1"/></circle>')


def segments(cx, cy, r, n, filled, color, width=10, gap_deg=6, colors=None):
    """Ring split into n arcs; the first `filled` are coloured. Good for counts."""
    out = ""
    span = 360 / n
    for i in range(n):
        a0 = math.radians(-90 + i * span + gap_deg / 2)
        a1 = math.radians(-90 + (i + 1) * span - gap_deg / 2)
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        large = 1 if span - gap_deg > 180 else 0
        col = (colors[i] if colors else color) if i < filled else LINE
        out += (f'<path d="M{x0:.2f} {y0:.2f} A{r} {r} 0 {large} 1 {x1:.2f} {y1:.2f}" fill="none" stroke="{col}" '
                f'stroke-width="{width}" stroke-linecap="butt" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{0.08 * i:.2f}s" fill="freeze"/></path>')
    return out


def donut(cx, cy, r, parts, width=22):
    total = sum(v for _, v, _ in parts)
    c = 2 * math.pi * r
    out, acc = "", 0.0
    for i, (_, v, col) in enumerate(parts):
        arc = c * v / total
        out += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="{width}" '
                f'stroke-dasharray="{max(arc - 2, 0.5):.2f} {c:.2f}" stroke-dashoffset="{-acc:.2f}" '
                f'transform="rotate(-90 {cx} {cy})" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{0.1 * i:.2f}s" fill="freeze"/></circle>')
        acc += arc
    return out


def arc_path(cx, cy, r, frac, max_deg=270):
    a0 = math.radians(-90)
    a1 = math.radians(-90 + max_deg * frac)
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    large = 1 if max_deg * frac > 180 else 0
    return f"M{x0:.2f} {y0:.2f} A{r} {r} 0 {large} 1 {x1:.2f} {y1:.2f}"


# ----------------------------------------------------------------------------- live data
def fetch_live(cache: dict) -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return cache

    def get(url):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
                                                   "Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)

    try:
        repos = [r for r in get(f"https://api.github.com/users/{USER}/repos?per_page=100") if not r["fork"]]
        langs: dict = {}
        for r in repos:
            for k, v in get(r["languages_url"]).items():
                langs[k] = langs.get(k, 0) + v
        live = {"public_repos": len(repos), "followers": get(f"https://api.github.com/users/{USER}")["followers"],
                "last_push": max(r["pushed_at"] for r in repos)[:10], "languages": langs}
    except Exception as e:  # network or rate-limit problem: keep the last good numbers
        print("GitHub API unavailable, using cache:", e)
        return cache
    (ROOT / "data" / "github_cache.json").write_text(json.dumps(live, indent=1))
    return live


# ----------------------------------------------------------------------------- banner
def banner(data):
    roles = ["Cybersecurity & IAM Analyst", "Security ML Engineer", "Data Scientist",
             "Fraud & Credit Risk Analyst", "Data Engineer (PySpark, Hive)"]
    n, per = len(roles), 3.0
    total = n * per
    role_svg = ""
    for i, r in enumerate(roles):
        a, b = i * per / total, (i + 1) * per / total
        vals, keys = "0;0;1;1;0;0", f"0;{a:.4f};{a + 0.02:.4f};{b - 0.03:.4f};{b - 0.01:.4f};1"
        if i == 0:
            vals, keys = "1;1;0;0;1", f"0;{b - 0.03:.4f};{b - 0.01:.4f};0.98;1"
        role_svg += (f'<text x="64" y="186" font-family="{MONO}" font-size="24" fill="url(#ember)" opacity="{1 if i == 0 else 0}">'
                     f'&gt; {esc(r)}<animate attributeName="opacity" values="{vals}" keyTimes="{keys}" '
                     f'dur="{total}s" repeatCount="indefinite"/></text>')
    # concentric "data collection" rings on the right
    cx, cy = 1010, 150
    rings = f'<circle cx="{cx}" cy="{cy}" r="150" fill="url(#soft)"/>'
    for i, (r, frac, col, dur) in enumerate([(118, 0.72, EMBER, 26), (94, 0.55, AMBER, 19), (70, 0.83, EMBER, 14), (46, 0.4, AMBER, 9)]):
        c = 2 * math.pi * r
        rings += (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LINE}" stroke-width="1"/>'
                  f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="{3 if i % 2 else 2}" '
                  f'stroke-linecap="round" stroke-dasharray="{frac * c:.1f} {c:.1f}" opacity="0.85">'
                  f'<animateTransform attributeName="transform" type="rotate" from="{0 if i % 2 else 360} {cx} {cy}" '
                  f'to="{360 if i % 2 else 0} {cx} {cy}" dur="{dur}s" repeatCount="indefinite"/></circle>')
    rnd = random.Random(11)
    for i in range(26):
        ang, rad = rnd.uniform(0, 2 * math.pi), rnd.choice([46, 70, 94, 118])
        x, y = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
        rings += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.choice([2, 2.5, 3.5])}" fill="{AMBER if i % 3 == 0 else EMBER}">'
                  f'<animate attributeName="opacity" values="0.2;1;0.2" dur="{2 + (i % 5) * 0.6:.1f}s" '
                  f'begin="{(i % 7) * 0.3:.1f}s" repeatCount="indefinite"/></circle>')
    rings += (t(cx, cy - 2, "16", 30, TEXT, 700, "middle") + t(cx, cy + 18, "REPOS", 10, MUTED, 600, "middle", MONO, ' letter-spacing="2"'))
    chips, x = "", 64
    for c in ["VIT Pune · B.Tech CE '26", "1 yr IAM & cybersecurity @ RNS", "Saviynt IGA · Zero Trust", "2 IEEE papers"]:
        w = 16 + len(c) * 7.4
        chips += (f'<rect x="{x:.0f}" y="226" width="{w:.0f}" height="30" rx="15" fill="{PANEL}" stroke="{LINE}"/>'
                  + t(x + w / 2, 246, c, 13, MUTED, 400, "middle"))
        x += w + 10
    body = (defs() + f'<rect width="1200" height="300" rx="18" fill="{BG}"/><rect width="1200" height="300" rx="18" fill="url(#grid)"/>'
            f'<rect width="1200" height="300" rx="18" fill="url(#glow)"/>{rings}'
            + t(64, 76, "HELLO, I'M", 15, DIM, 400, font=MONO, extra=' letter-spacing="3"')
            + t(62, 138, "Shubhan Punde", 62, TEXT, 700)
            + f'{role_svg}{chips}<rect x="0" y="296" width="1200" height="4" fill="url(#ember)"/>')
    return svg(1200, 300, body, "Shubhan Punde: cybersecurity & IAM, security ML, data science")


# ----------------------------------------------------------------------------- profile dashboard (circles)
def dashboard(data, projects, tracks):
    W, H = 1200, 470
    tested = sum(p["tests"] for p in projects)
    b = defs() + f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/><rect width="{W}" height="{H}" rx="18" fill="url(#grid)"/>'
    b += (t(40, 52, "Profile analytics", 22, TEXT, 700)
          + t(1160, 52, f"auto-refreshed {dt.date.today():%d %b %Y} · last push {data['last_push']}", 12, DIM, 400, "end", MONO))

    # panel 1: four circular KPIs
    px, pw = 40, 360
    b += f'<rect x="{px}" y="76" width="{pw}" height="366" rx="14" fill="{PANEL}" stroke="{LINE}"/>'
    b += t(px + 24, 106, "At a glance", 15, TEXT, 600)
    kpis = [
        ("ring", tested / len(projects), f"{tested}/{len(projects)}", "projects CI-tested", EMBER),
        ("seg", (3, 3, [EMBER, EMBER, AMBER]), "3", "papers · 2 IEEE", AMBER),
        ("seg", (12, 12, None), "12 mo", "IAM & security role", EMBER),
        ("ring", 1.0, str(data["public_repos"]), "public repositories", AMBER),
    ]
    for i, (kind, val, big, label, col) in enumerate(kpis):
        cx = px + 95 + (i % 2) * 170
        cy = 190 + (i // 2) * 140
        b += f'<circle cx="{cx}" cy="{cy}" r="58" fill="url(#soft)"/>'
        if kind == "ring":
            b += ring(cx, cy, 46, val, col, 9, delay=0.15 * i)
        else:
            n, filled, cols = val
            b += segments(cx, cy, 46, n, filled, col, 9, gap_deg=8 if n > 6 else 10, colors=cols)
        b += t(cx, cy + 7, big, 21 if len(big) < 5 else 17, TEXT, 700, "middle")
        b += t(cx, cy + 76, label, 12, MUTED, 400, "middle")

    # panel 2: language donut
    px2 = px + pw + 20
    b += f'<rect x="{px2}" y="76" width="{pw}" height="366" rx="14" fill="{PANEL}" stroke="{LINE}"/>'
    b += t(px2 + 24, 106, "Code by language", 15, TEXT, 600) + t(px2 + pw - 24, 106, "bytes", 11, DIM, 400, "end", MONO)
    langs = {k: v for k, v in data["languages"].items() if k not in ("Makefile", "Dockerfile", "Shell")}
    total = sum(langs.values())
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
    other = total - sum(v for _, v in top)
    if other > 0:
        top.append(("Other", other))
    parts = [(k, v, LANG_COLORS.get(k, "#57534E")) for k, v in top]
    dcx, dcy = px2 + 104, 250
    b += f'<circle cx="{dcx}" cy="{dcy}" r="92" fill="url(#soft)"/>' + donut(dcx, dcy, 66, parts, 24)
    b += t(dcx, dcy - 2, str(len(langs)), 30, TEXT, 700, "middle") + t(dcx, dcy + 18, "languages", 11, MUTED, 400, "middle")
    for i, (k, v, col) in enumerate(parts):
        ly = 168 + i * 26
        b += (f'<circle cx="{px2 + 214}" cy="{ly - 4}" r="5" fill="{col}"/>' + t(px2 + 226, ly, k, 12.5, TEXT)
              + t(px2 + pw - 24, ly, f"{100 * v / total:.1f}%", 12, MUTED, 400, "end", MONO))

    # panel 3: radial bars per role track
    px3 = px2 + pw + 20
    b += f'<rect x="{px3}" y="76" width="{pw}" height="366" rx="14" fill="{PANEL}" stroke="{LINE}"/>'
    b += t(px3 + 24, 106, "Projects per role", 15, TEXT, 600) + t(px3 + pw - 24, 106, "radial bars", 11, DIM, 400, "end", MONO)
    counts = sorted(((k, sum(k in p["tracks"] for p in projects)) for k in tracks), key=lambda kv: -kv[1])
    mx = max(c for _, c in counts)
    rcx, rcy = px3 + 200, 262
    for i, (k, c) in enumerate(counts):
        r = 112 - i * 15
        col = tracks[k]["color"]
        b += (f'<path d="{arc_path(rcx, rcy, r, 1.0)}" fill="none" stroke="{LINE}" stroke-width="9" stroke-linecap="round"/>'
              f'<path d="{arc_path(rcx, rcy, r, c / mx)}" fill="none" stroke="{col}" stroke-width="9" stroke-linecap="round" '
              f'opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{0.1 * i:.1f}s" fill="freeze"/></path>')
        b += t(rcx - 6, rcy - r + 4, f"{tracks[k]['short']}  {c}", 10.5, col, 600, "end")
    b += t(rcx, rcy + 6, f"{len(projects)}", 26, TEXT, 700, "middle") + t(rcx, rcy + 24, "projects", 11, MUTED, 400, "middle")
    b += t(px3 + pw - 24, 428, "a project can count for several roles", 10.5, DIM, 400, "end")
    return svg(W, H, b, "Profile analytics: CI coverage, papers, experience, languages and projects per role")


# ----------------------------------------------------------------------------- experience timeline
def timeline():
    W, H = 1200, 260
    events = [
        ("Nov 2022", "B.Tech starts", "VIT Pune · CE", AMBER, 10),
        ("Sep 2023", "Cybersecurity intern", "Skolar · 500+ endpoints", EMBER, 12),
        ("Jun 2024", "IEEE ICCCNT paper", "YOLOv8 traffic", AMBER, 10),
        ("Jul 2024", "Research intern", "UNLV, USA · forecasting", EMBER, 13),
        ("Dec 2024", "IEEE ICICNIS paper", "Cyberbullying ensemble", AMBER, 10),
        ("Jul 2025", "IAM & cybersecurity", "RNS Technology · 1 yr", EMBER, 17),
        ("May 2026", "Saviynt ISAA", "certified", AMBER, 10),
        ("Jun 2026", "Graduated", "CGPA 8.14", AMBER, 11),
        ("Now", "Open to roles", "India · U.S. · remote", "#4ADE80", 14),
    ]
    b = defs() + f'<rect width="{W}" height="{H}" rx="18" fill="{BG}"/>'
    b += t(40, 46, "Journey", 20, TEXT, 700) + t(1160, 46, "bigger circle = longer / bigger milestone", 11, DIM, 400, "end", MONO)
    y = 142
    x0, x1 = 80, 1120
    b += f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{LINE}" stroke-width="3"/>'
    b += (f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="url(#ember)" stroke-width="3" stroke-dasharray="{x1 - x0}" '
          f'stroke-dashoffset="{x1 - x0}"><animate attributeName="stroke-dashoffset" from="{x1 - x0}" to="0" dur="2s" fill="freeze"/></line>')
    step = (x1 - x0) / (len(events) - 1)
    for i, (when, what, sub, col, r) in enumerate(events):
        x = x0 + i * step
        up = i % 2 == 0
        b += (f'<circle cx="{x:.1f}" cy="{y}" r="{r + 7}" fill="{col}" opacity="0.15"/>'
              f'<circle cx="{x:.1f}" cy="{y}" r="{r}" fill="{BG}" stroke="{col}" stroke-width="3"/>'
              f'<circle cx="{x:.1f}" cy="{y}" r="{max(r - 7, 3)}" fill="{col}">'
              f'<animate attributeName="r" values="{max(r - 7, 3)};{max(r - 5, 4)};{max(r - 7, 3)}" dur="2.4s" begin="{0.2 * i:.1f}s" repeatCount="indefinite"/></circle>')
        ty = y - r - 50 if up else y + r + 24
        b += (t(x, ty, when, 11, col, 600, "middle", MONO) + t(x, ty + 16, what, 12.5, TEXT, 600, "middle")
              + t(x, ty + 31, sub, 10.5, MUTED, 400, "middle"))
    return svg(W, H, b, "Journey timeline from 2022 to now")


# ----------------------------------------------------------------------------- role x project matrix
def matrix(projects, tracks):
    keys = list(tracks)
    cw, rh, left, top = 96, 30, 300, 100
    w, h = left + cw * len(keys) + 40, top + rh * len(projects) + 30
    b = defs() + f'<rect width="{w}" height="{h}" rx="18" fill="{BG}"/>'
    b += (t(32, 44, "Which project proves which role", 20, TEXT, 700)
          + t(32, 68, "Pick the column for the job you are hiring for. Big dot = main focus, small dot = also relevant.", 13, MUTED))
    for j, k in enumerate(keys):
        b += t(left + j * cw + cw / 2, top - 10, tracks[k]["short"], 12, tracks[k]["color"], 600, "middle")
    for i, p in enumerate(projects):
        y = top + i * rh
        if i % 2 == 0:
            b += f'<rect x="20" y="{y}" width="{w - 40}" height="{rh}" rx="6" fill="{PANEL}"/>'
        b += t(32, y + 20, p["title"], 13)
        for j, k in enumerate(keys):
            cx, cy = left + j * cw + cw / 2, y + rh / 2
            if k in p["tracks"]:
                primary = p["tracks"][0] == k
                col = tracks[k]["color"]
                if primary:
                    b += (f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="10" fill="{col}" opacity="0.18"/>'
                          f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="6.5" fill="{col}"/>')
                else:
                    b += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="5" fill="none" stroke="{col}" stroke-width="2" opacity="0.8"/>'
            else:
                b += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="2" fill="{LINE}"/>'
    return svg(w, h, b, "Role by project matrix")


# ----------------------------------------------------------------------------- project cards (ring gauge)
def card(p, tracks):
    W, H = 560, 232
    col = tracks[p["tracks"][0]]["color"]
    rg = p["ring"]
    b = defs() + (f'<clipPath id="c"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16"/></clipPath>'
                  f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{BG}" stroke="{LINE}"/>'
                  f'<rect x="0" y="0" width="{W}" height="5" fill="{col}" clip-path="url(#c)"/>'
                  f'<circle cx="92" cy="128" r="90" fill="url(#soft)" clip-path="url(#c)"/>')
    # gauge
    cx, cy = 92, 122
    b += ring(cx, cy, 54, rg["frac"], col, 11, dashed=rg.get("dashed", False))
    b += f'<circle cx="{cx}" cy="{cy}" r="40" fill="{PANEL}"/>'
    v = rg["value"]
    b += t(cx, cy + 6, v, 20 if len(v) <= 5 else 16, TEXT, 700, "middle")
    b += t(cx, cy + 82, rg["label"], 11.5, MUTED, 400, "middle")
    # right side
    x = 180
    for tk in p["tracks"]:
        label = tracks[tk]["short"]
        w = 18 + len(label) * 6.6
        b += (f'<rect x="{x:.0f}" y="22" width="{w:.0f}" height="22" rx="11" fill="{tracks[tk]["color"]}" fill-opacity="0.14" '
              f'stroke="{tracks[tk]["color"]}" stroke-opacity="0.5"/>' + t(x + w / 2, 37, label, 11, tracks[tk]["color"], 600, "middle"))
        x += w + 8
    b += t(180, 76, p["title"], 19, TEXT, 700)
    b += t(180, 98, p["tagline"][:62] + ("…" if len(p["tagline"]) > 62 else ""), 12, MUTED)
    for i, (val, lab) in enumerate(p["metrics"][1:3]):
        mx = 180 + i * 182
        b += (f'<rect x="{mx}" y="114" width="170" height="58" rx="10" fill="{PANEL}" stroke="{LINE}"/>'
              f'<circle cx="{mx + 20}" cy="143" r="5" fill="{col}" opacity="0.9"/>'
              + t(mx + 34, 143, val, 17, TEXT, 700) + t(mx + 34, 160, lab, 11, MUTED))
    status = "● tests passing in CI" if p["tests"] else "◌ in development"
    b += t(180, 194, "  ·  ".join(p["stack"]), 11.5, DIM, 400, font=MONO)
    b += t(180, 214, status, 10.5, "#4ADE80" if p["tests"] else AMBER, 400, font=MONO)
    b += t(W - 22, 214, "View repo →", 12, col, 600, "end")
    return svg(W, H, b, f'{p["title"]}: {p["tagline"]}')


# ----------------------------------------------------------------------------- section header + footer
def header(text, sub):
    b = defs() + (f'<circle cx="14" cy="50" r="12" fill="none" stroke="{EMBER}" stroke-width="3"/>'
                  f'<circle cx="14" cy="50" r="4" fill="{AMBER}"/>'
                  + t(38, 58, text, 26, EMBER, 700) + t(38, 84, sub, 14, MUTED))
    return svg(1200, 96, b, text)


def footer():
    b = defs() + (f'<path d="M0 40 Q 150 0 300 30 T 600 30 T 900 30 T 1200 20 V 90 H 0 Z" fill="url(#ember)" opacity="0.9">'
                  f'<animate attributeName="d" dur="8s" repeatCount="indefinite" values="'
                  f'M0 40 Q 150 0 300 30 T 600 30 T 900 30 T 1200 20 V 90 H 0 Z;'
                  f'M0 30 Q 150 55 300 30 T 600 35 T 900 25 T 1200 35 V 90 H 0 Z;'
                  f'M0 40 Q 150 0 300 30 T 600 30 T 900 30 T 1200 20 V 90 H 0 Z"/></path>'
                  + t(600, 76, "Open to Cybersecurity · IAM · Security ML · Data Science · Risk · Data Engineering roles  ·  India / U.S. / remote",
                      14, BG, 600, "middle"))
    return svg(1200, 90, b, "Open to roles")


def main():
    cfg = json.loads((ROOT / "data" / "projects.json").read_text())
    tracks, projects = cfg["tracks"], cfg["projects"]
    data = fetch_live(json.loads((ROOT / "data" / "github_cache.json").read_text()))
    (ASSETS / "projects").mkdir(parents=True, exist_ok=True)
    (ASSETS / "banner.svg").write_text(banner(data))
    (ASSETS / "dashboard.svg").write_text(dashboard(data, projects, tracks))
    (ASSETS / "timeline.svg").write_text(timeline())
    (ASSETS / "role-matrix.svg").write_text(matrix(projects, tracks))
    (ASSETS / "footer.svg").write_text(footer())
    for name, (ti, s) in {"about": ("About me", "Who I am and what I build"),
                          "work": ("Work by role", "Every project ends in a decision someone can act on, with measured results"),
                          "stack": ("Toolkit", "What I use, grouped by job"),
                          "pubs": ("Publications & certifications", "Peer-reviewed work and credentials")}.items():
        (ASSETS / f"h-{name}.svg").write_text(header(ti, s))
    for p in projects:
        (ASSETS / "projects" / f'{p["id"]}.svg').write_text(card(p, tracks))
    print("built", len(projects), "cards")


if __name__ == "__main__":
    main()
