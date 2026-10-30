"""Builds every SVG on the profile README.

Static parts come from data/projects.json. Live parts (repo count, language
mix, last activity) come from the GitHub API when GITHUB_TOKEN is set (the
scheduled Action does this); otherwise data/github_cache.json is used.

    python scripts/build_profile.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
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


def defs():
    return (f'<defs><linearGradient id="ember" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0" stop-color="{EMBER}"/><stop offset="1" stop-color="{AMBER}"/></linearGradient>'
            f'<radialGradient id="glow" cx="0.85" cy="0.35" r="0.6"><stop offset="0" stop-color="{EMBER}" stop-opacity="0.35"/>'
            f'<stop offset="1" stop-color="{EMBER}" stop-opacity="0"/></radialGradient>'
            f'<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">'
            f'<path d="M32 0H0V32" fill="none" stroke="#FFFFFF" stroke-opacity="0.035"/></pattern></defs>')


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
    roles = ["Data Scientist", "Fraud & Credit Risk Analyst", "Security / Detection Engineer",
             "Data Engineer (PySpark, Hive)", "ML & Backend Engineer"]
    n, per = len(roles), 3.0
    total = n * per
    role_svg = ""
    for i, r in enumerate(roles):
        a, b = i * per / total, (i + 1) * per / total
        vals = "0;0;1;1;0;0"
        keys = f"0;{max(a, 0):.4f};{a + 0.02:.4f};{b - 0.03:.4f};{b - 0.01:.4f};1"
        if i == 0:
            vals, keys = "1;1;0;0;1", f"0;{b - 0.03:.4f};{b - 0.01:.4f};0.98;1"
        role_svg += (f'<text x="64" y="186" font-family="{MONO}" font-size="24" fill="url(#ember)" opacity="{1 if i == 0 else 0}">'
                     f'&gt; {esc(r)}<animate attributeName="opacity" values="{vals}" keyTimes="{keys}" '
                     f'dur="{total}s" repeatCount="indefinite"/></text>')
    # network motif on the right
    import random
    rnd = random.Random(7)
    pts = [(rnd.randint(800, 1150), rnd.randint(40, 290)) for _ in range(22)]
    edges = ""
    for i, (x, y) in enumerate(pts):
        near = sorted(pts, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)[1:3]
        for (x2, y2) in near:
            edges += f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" stroke="{EMBER}" stroke-opacity="0.22"/>'
    nodes = ""
    for i, (x, y) in enumerate(pts):
        r = 2.5 + (i % 3)
        col = AMBER if i % 4 == 0 else EMBER
        nodes += (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{col}"><animate attributeName="opacity" '
                  f'values="0.35;1;0.35" dur="{2.5 + (i % 5) * 0.7:.1f}s" begin="{(i % 7) * 0.4:.1f}s" repeatCount="indefinite"/></circle>')
    chips, x = "", 64
    for c in ["VIT Pune · B.Tech CE '26", "1 yr risk analytics @ RNS Technology", "3 publications · 2 IEEE",
              f"{data['public_repos']} public repos · CI-tested"]:
        w = 14 + len(c) * 7.6
        chips += (f'<rect x="{x}" y="226" width="{w:.0f}" height="30" rx="15" fill="{PANEL}" stroke="{LINE}"/>'
                  f'<text x="{x + w / 2:.0f}" y="246" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(c)}</text>')
        x += w + 10
    body = (defs() + f'<rect width="1200" height="300" rx="18" fill="{BG}"/><rect width="1200" height="300" rx="18" fill="url(#grid)"/>'
            f'<rect width="1200" height="300" rx="18" fill="url(#glow)"/>{edges}{nodes}'
            f'<text x="64" y="76" font-family="{MONO}" font-size="15" fill="{DIM}" letter-spacing="3">HELLO, I\'M</text>'
            f'<text x="62" y="138" font-family="{SANS}" font-size="62" font-weight="700" fill="{TEXT}">Shubhan Punde</text>'
            f'{role_svg}{chips}<rect x="0" y="296" width="1200" height="4" fill="url(#ember)"/>')
    return svg(1200, 300, body, "Shubhan Punde: data science, risk analytics, security and engineering")


# ----------------------------------------------------------------------------- profile dashboard
def dashboard(data, projects, tracks):
    tested = sum(p["tests"] for p in projects)
    langs = {k: v for k, v in data["languages"].items() if k not in ("Makefile", "Dockerfile", "Shell")}
    total = sum(langs.values())
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:7]
    other = total - sum(v for _, v in top)
    if other > 0:
        top.append(("Other", other))
    kpis = [(str(data["public_repos"]), "public repositories"), (f"{tested}/{len(projects)}", "projects with CI tests"),
            ("3", "publications (2 IEEE)"), (str(len(langs)), "languages shipped"),
            (str(len(tracks)), "role tracks covered"), ("1 yr", "industry, risk analytics")]
    b = defs() + f'<rect width="1200" height="430" rx="18" fill="{BG}"/><rect width="1200" height="430" rx="18" fill="url(#grid)"/>'
    b += (f'<text x="40" y="52" font-family="{SANS}" font-size="22" font-weight="700" fill="{TEXT}">Profile analytics</text>'
          f'<text x="1160" y="52" text-anchor="end" font-family="{MONO}" font-size="12" fill="{DIM}">auto-refreshed {dt.date.today():%d %b %Y} · last push {data["last_push"]}</text>')
    tw = (1200 - 80 - 5 * 16) / 6
    for i, (v, l) in enumerate(kpis):
        x = 40 + i * (tw + 16)
        b += (f'<rect x="{x:.0f}" y="76" width="{tw:.0f}" height="96" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
              f'<rect x="{x:.0f}" y="76" width="4" height="96" rx="2" fill="url(#ember)"/>'
              f'<text x="{x + 20:.0f}" y="122" font-family="{SANS}" font-size="32" font-weight="700" fill="{TEXT}">{esc(v)}</text>'
              f'<text x="{x + 20:.0f}" y="150" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(l)}</text>')
    # language mix (left)
    b += (f'<rect x="40" y="192" width="548" height="210" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
          f'<text x="64" y="224" font-family="{SANS}" font-size="15" font-weight="600" fill="{TEXT}">Code by language</text>'
          f'<text x="564" y="224" text-anchor="end" font-family="{MONO}" font-size="11" fill="{DIM}">bytes, all public repos</text>')
    x = 64.0
    for k, v in top:
        w = 500 * v / total
        b += f'<rect x="{x:.1f}" y="242" width="{max(w - 2, 1):.1f}" height="14" rx="3" fill="{LANG_COLORS.get(k, "#57534E")}"/>'
        x += w
    for i, (k, v) in enumerate(top):
        cx, cy = 64 + (i % 2) * 250, 288 + (i // 2) * 28
        b += (f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{LANG_COLORS.get(k, "#57534E")}"/>'
              f'<text x="{cx + 18}" y="{cy}" font-family="{SANS}" font-size="13" fill="{TEXT}">{esc(k)}</text>'
              f'<text x="{cx + 220}" y="{cy}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{MUTED}">{100 * v / total:.1f}%</text>')
    # role coverage (right)
    b += (f'<rect x="612" y="192" width="548" height="210" rx="12" fill="{PANEL}" stroke="{LINE}"/>'
          f'<text x="636" y="224" font-family="{SANS}" font-size="15" font-weight="600" fill="{TEXT}">Projects per role track</text>'
          f'<text x="1136" y="224" text-anchor="end" font-family="{MONO}" font-size="11" fill="{DIM}">a project can count for several</text>')
    counts = {t: sum(t in p["tracks"] for p in projects) for t in tracks}
    mx = max(counts.values())
    for i, (t, c) in enumerate(sorted(counts.items(), key=lambda kv: -kv[1])):
        y = 246 + i * 22
        w = 280 * c / mx
        b += (f'<text x="636" y="{y + 11}" font-family="{SANS}" font-size="12.5" fill="{MUTED}">{esc(tracks[t]["name"])}</text>'
              f'<rect x="836" y="{y}" width="280" height="13" rx="4" fill="{LINE}"/>'
              f'<rect x="836" y="{y}" width="{w:.0f}" height="13" rx="4" fill="{tracks[t]["color"]}">'
              f'<animate attributeName="width" from="0" to="{w:.0f}" dur="1.2s" fill="freeze"/></rect>'
              f'<text x="1136" y="{y + 11}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{TEXT}">{c}</text>')
    return svg(1200, 430, b, "Profile analytics dashboard")


# ----------------------------------------------------------------------------- role x project matrix
def matrix(projects, tracks):
    keys = list(tracks)
    cw, rh, left, top = 96, 30, 300, 100
    w, h = left + cw * len(keys) + 40, top + rh * len(projects) + 30
    b = defs() + f'<rect width="{w}" height="{h}" rx="18" fill="{BG}"/>'
    b += (f'<text x="32" y="44" font-family="{SANS}" font-size="20" font-weight="700" fill="{TEXT}">Which project proves which role</text>'
          f'<text x="32" y="68" font-family="{SANS}" font-size="13" fill="{MUTED}">Filled cell = the project is evidence for that role. Pick the column for the job you are hiring for.</text>')
    for j, k in enumerate(keys):
        cx = left + j * cw + cw / 2
        b += f'<text x="{cx:.0f}" y="{top - 10}" text-anchor="middle" font-family="{SANS}" font-size="12" font-weight="600" fill="{tracks[k]["color"]}">{esc(tracks[k]["short"])}</text>'
    for i, p in enumerate(projects):
        y = top + i * rh
        if i % 2 == 0:
            b += f'<rect x="20" y="{y}" width="{w - 40}" height="{rh}" rx="6" fill="{PANEL}"/>'
        b += f'<text x="32" y="{y + 20}" font-family="{SANS}" font-size="13" fill="{TEXT}">{esc(p["title"])}</text>'
        for j, k in enumerate(keys):
            cx, cy = left + j * cw + cw / 2, y + rh / 2
            if k in p["tracks"]:
                primary = p["tracks"][0] == k
                b += (f'<rect x="{cx - 20:.0f}" y="{cy - 8:.0f}" width="40" height="16" rx="8" fill="{tracks[k]["color"]}" '
                      f'opacity="{1 if primary else 0.45}"/>')
            else:
                b += f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="2" fill="{LINE}"/>'
    b += (f'<rect x="{w - 260}" y="{h - 22}" width="24" height="10" rx="5" fill="{EMBER}"/><text x="{w - 230}" y="{h - 13}" font-family="{SANS}" font-size="11" fill="{MUTED}">primary</text>'
          f'<rect x="{w - 170}" y="{h - 22}" width="24" height="10" rx="5" fill="{EMBER}" opacity="0.45"/><text x="{w - 140}" y="{h - 13}" font-family="{SANS}" font-size="11" fill="{MUTED}">also relevant</text>')
    return svg(w, h, b, "Role by project matrix")


# ----------------------------------------------------------------------------- project cards
def card(p, tracks):
    W, H = 560, 230
    col = tracks[p["tracks"][0]]["color"]
    b = defs() + (f'<clipPath id="c"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16"/></clipPath>'
                  f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="{BG}" stroke="{LINE}"/>'
                  f'<rect x="0" y="0" width="{W}" height="5" fill="{col}" clip-path="url(#c)"/>')
    x = 24
    for t in p["tracks"]:
        label = tracks[t]["short"]
        w = 18 + len(label) * 6.6
        b += (f'<rect x="{x}" y="22" width="{w:.0f}" height="22" rx="11" fill="{tracks[t]["color"]}" fill-opacity="0.14" stroke="{tracks[t]["color"]}" stroke-opacity="0.5"/>'
              f'<text x="{x + w / 2:.0f}" y="37" text-anchor="middle" font-family="{SANS}" font-size="11" font-weight="600" fill="{tracks[t]["color"]}">{esc(label)}</text>')
        x += w + 8
    if p["tests"]:
        b += f'<text x="{W - 24}" y="37" text-anchor="end" font-family="{MONO}" font-size="11" fill="#4ADE80">● tests passing in CI</text>'
    b += (f'<text x="24" y="78" font-family="{SANS}" font-size="21" font-weight="700" fill="{TEXT}">{esc(p["title"])}</text>'
          f'<text x="24" y="102" font-family="{SANS}" font-size="13" fill="{MUTED}">{esc(p["tagline"])}</text>')
    mw = (W - 48 - 2 * 12) / 3
    for i, (v, l) in enumerate(p["metrics"]):
        mx = 24 + i * (mw + 12)
        b += (f'<rect x="{mx:.0f}" y="118" width="{mw:.0f}" height="66" rx="10" fill="{PANEL}" stroke="{LINE}"/>'
              f'<text x="{mx + 14:.0f}" y="152" font-family="{SANS}" font-size="24" font-weight="700" fill="{col if i == 0 else TEXT}">{esc(v)}</text>'
              f'<text x="{mx + 14:.0f}" y="172" font-family="{SANS}" font-size="12" fill="{MUTED}">{esc(l)}</text>')
    b += f'<text x="24" y="210" font-family="{MONO}" font-size="12" fill="{DIM}">{esc("  ·  ".join(p["stack"]))}</text>'
    b += f'<text x="{W - 24}" y="210" text-anchor="end" font-family="{SANS}" font-size="12" font-weight="600" fill="{col}">View repo →</text>'
    return svg(W, H, b, f'{p["title"]}: {p["tagline"]}')


# ----------------------------------------------------------------------------- section header + footer
def header(text, sub):
    b = defs() + (f'<rect x="0" y="34" width="6" height="30" rx="3" fill="url(#ember)"/>'
                  f'<text x="20" y="58" font-family="{SANS}" font-size="26" font-weight="700" fill="{EMBER}">{esc(text)}</text>'
                  f'<text x="20" y="84" font-family="{SANS}" font-size="14" fill="{MUTED}">{esc(sub)}</text>')
    return svg(1200, 96, b, text)


def footer():
    b = defs() + (f'<path d="M0 40 Q 150 0 300 30 T 600 30 T 900 30 T 1200 20 V 90 H 0 Z" fill="url(#ember)" opacity="0.9">'
                  f'<animate attributeName="d" dur="8s" repeatCount="indefinite" values="'
                  f'M0 40 Q 150 0 300 30 T 600 30 T 900 30 T 1200 20 V 90 H 0 Z;'
                  f'M0 30 Q 150 55 300 30 T 600 35 T 900 25 T 1200 35 V 90 H 0 Z;'
                  f'M0 40 Q 150 0 300 30 T 600 30 T 900 30 T 1200 20 V 90 H 0 Z"/></path>'
                  f'<text x="600" y="76" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="600" fill="{BG}">'
                  f'Open to Data Science · Risk · Security · Data Engineering · Software roles  ·  Pune / relocate</text>')
    return svg(1200, 90, b, "Open to roles")


def main():
    cfg = json.loads((ROOT / "data" / "projects.json").read_text())
    tracks, projects = cfg["tracks"], cfg["projects"]
    data = fetch_live(json.loads((ROOT / "data" / "github_cache.json").read_text()))
    (ASSETS / "projects").mkdir(parents=True, exist_ok=True)
    (ASSETS / "banner.svg").write_text(banner(data))
    (ASSETS / "dashboard.svg").write_text(dashboard(data, projects, tracks))
    (ASSETS / "role-matrix.svg").write_text(matrix(projects, tracks))
    (ASSETS / "footer.svg").write_text(footer())
    for name, (t, s) in {"about": ("About me", "Who I am and what I build"),
                         "work": ("Work by role", "Every project ends in a decision someone can act on, with measured results"),
                         "stack": ("Toolkit", "What I use, grouped by job"),
                         "pubs": ("Publications & certifications", "Peer-reviewed work and credentials")}.items():
        (ASSETS / f"h-{name}.svg").write_text(header(t, s))
    for p in projects:
        (ASSETS / "projects" / f'{p["id"]}.svg').write_text(card(p, tracks))
    print("built", len(projects), "cards")


if __name__ == "__main__":
    main()
