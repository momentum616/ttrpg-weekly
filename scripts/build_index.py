"""
build_index.py
Scans /reports for HTML files and:
1. Regenerates index.html in the Dungeon Economy design system
2. Injects prev/next nav + back-to-index link into each report's topbar

Run automatically by GitHub Actions when a new report is pushed.
"""

import re
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path("reports")
reports = sorted(REPORTS_DIR.glob("*.html"), reverse=True)
total = len(reports)
slugs = [p.stem for p in reports]


# ── Helpers ───────────────────────────────────────────────────────────────────

def slug_to_display(slug):
    try:
        return datetime.strptime(slug, "%Y-%m-%d").strftime("%B %d, %Y")
    except ValueError:
        return slug


def extract_meta(path):
    """Pull issue number, top headline, and preview text from HTML."""
    text = path.read_text(encoding="utf-8", errors="ignore")

    issue_match = re.search(r'Issue\s*#(\d+)', text)
    issue = issue_match.group(1) if issue_match else "—"

    headlines = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', text, re.DOTALL)
    headlines = [re.sub(r'<[^>]+>', '', h).strip() for h in headlines if len(h.strip()) > 25]
    title = headlines[0] if headlines else "Weekly D&D intelligence brief"

    paras = re.findall(r'<p[^>]*>(.*?)</p>', text, re.DOTALL)
    preview = ""
    for p in paras:
        clean = re.sub(r'<[^>]+>', '', p).strip()
        if len(clean) > 60:
            preview = clean[:160]
            break
    if not preview:
        preview = "D&D publishing, platforms, and market signals."

    return issue, title[:110], preview


# ── Nav CSS block (injected once per report if absent) ────────────────────────

NAV_CSS = """  <style id="de-nav-style">
    .de-home-btn {
      display: inline-flex; align-items: center; gap: 7px;
      font-size: 0.95rem; font-weight: 600; color: var(--text);
      text-decoration: none; letter-spacing: 0.01em;
    }
    .de-home-btn:hover { color: var(--accent); text-decoration: none; }
    .de-nav-group { display: flex; align-items: center; gap: 8px; }
    .de-nav-btn {
      display: inline-flex; align-items: center; gap: 6px;
      padding: 8px 14px; border-radius: 999px;
      border: 1px solid var(--line); background: var(--bg-elev);
      color: var(--muted); font-size: 0.82rem; font-weight: 600;
      text-decoration: none; transition: border-color .15s, color .15s;
      white-space: nowrap;
    }
    .de-nav-btn:hover { border-color: color-mix(in srgb, var(--accent) 42%, var(--line)); color: var(--accent); text-decoration: none; }
    .de-nav-btn.disabled { opacity: 0.35; pointer-events: none; }
    .de-nav-divider { width: 1px; height: 18px; background: var(--line); margin: 0 2px; }
  </style>"""


def build_topbar_inner(i, slugs):
    """Return the full topbar-inner content for report at index i."""
    prev_slug = slugs[i + 1] if i + 1 < len(slugs) else None
    next_slug = slugs[i - 1] if i - 1 >= 0 else None

    prev_href = f"../{REPORTS_DIR.name}/{prev_slug}.html" if prev_slug else "#"
    next_href = f"../{REPORTS_DIR.name}/{next_slug}.html" if next_slug else "#"

    prev_cls = "de-nav-btn" + ("" if prev_slug else " disabled")
    next_cls = "de-nav-btn" + ("" if next_slug else " disabled")

    return (
        f'\n      <a href="../index.html" class="de-home-btn" aria-label="Back to archive">'
        f'\n        <span class="brand-dot" aria-hidden="true"></span>'
        f'\n        <strong>The Dungeon Economy</strong>'
        f'\n      </a>'
        f'\n      <div class="de-nav-group">'
        f'\n        <a href="{prev_href}" class="{prev_cls}">← Previous</a>'
        f'\n        <span class="de-nav-divider" aria-hidden="true"></span>'
        f'\n        <a href="{next_href}" class="{next_cls}">Next →</a>'
        f'\n        <button class="toggle" id="themeToggle" type="button" aria-label="Toggle theme">Light mode</button>'
        f'\n      </div>'
    )


def inject_nav_into_report(path, i, slugs):
    """Rewrite the topbar block in a report with correct nav + theme toggle."""
    text = path.read_text(encoding="utf-8", errors="ignore")

    # Inject nav CSS after the last </style> in <head> if not already there
    if 'id="de-nav-style"' not in text:
        text = re.sub(r'(</style>)(\s*</head>)', lambda m: m.group(1) + '\n' + NAV_CSS + m.group(2), text, count=1)

    new_inner = build_topbar_inner(i, slugs)

    # Replace the full content of the topbar div (handles both wrap and non-wrap variants)
    # Strategy: find the topbar div, find its inner content up to </div>, replace it
    text = re.sub(
        r'(<div class="(?:wrap )?topbar-inner">)(.*?)(</div>\s*</div>)',
        lambda m: m.group(1) + new_inner + '\n    ' + m.group(3),
        text,
        count=1,
        flags=re.DOTALL
    )

    path.write_text(text, encoding="utf-8")
    print(f"  Nav updated: {path.name}")


# Inject nav into all reports
for i, path in enumerate(reports):
    inject_nav_into_report(path, i, slugs)


# ── Build archive cards ───────────────────────────────────────────────────────

cards_html = ""
for i, path in enumerate(reports):
    slug = path.stem
    display = slug_to_display(slug)
    issue, title, preview = extract_meta(path)
    is_latest = (i == 0)

    latest_class = " latest" if is_latest else ""
    latest_badge = '<span class="latest-badge">Latest</span>' if is_latest else ""

    cards_html += f"""
      <a href="reports/{slug}.html" class="issue-card{latest_class}">
        <div class="card-top">
          <span class="issue-num">Issue #{issue}</span>
          {latest_badge}
        </div>
        <div class="card-date">{display}</div>
        <div class="card-title">{title}</div>
        <div class="card-preview">{preview}…</div>
        <div class="card-arrow">Read issue →</div>
      </a>"""

if not cards_html:
    cards_html = """
      <div class="empty-state">
        <p>No reports yet. Drop your first dated HTML file into /reports to get started.</p>
      </div>"""


# ── Generate index.html ───────────────────────────────────────────────────────

index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>The Dungeon Economy — Archive</title>
  <meta name="description" content="Archive of The Dungeon Economy — a weekly brief on D&D, publishing, platforms, and market signals." />
  <style>
    :root {{
      --bg: #0c0f14;
      --bg-elev: #121722;
      --card: rgba(255,255,255,0.04);
      --line: rgba(255,255,255,0.10);
      --text: #edf2f8;
      --muted: #aeb8ca;
      --soft: #8e98ab;
      --accent: #8ab4ff;
      --accent-2: #93f0c8;
      --shadow: 0 18px 44px rgba(0,0,0,0.28);
      --radius: 18px;
      --max: 1220px;
    }}
    html[data-theme="light"] {{
      --bg: #f4eee4;
      --bg-elev: #fbf7ef;
      --card: rgba(74,56,28,0.05);
      --line: rgba(74,56,28,0.12);
      --text: #211a14;
      --muted: #605648;
      --soft: #7d7163;
      --accent: #245dc5;
      --accent-2: #0a8b69;
      --shadow: 0 14px 34px rgba(82,59,28,0.10);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(138,180,255,0.11), transparent 28%),
        radial-gradient(circle at top right, rgba(147,240,200,0.08), transparent 22%),
        var(--bg);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.58; -webkit-font-smoothing: antialiased; min-height: 100vh;
    }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .wrap {{ width: min(var(--max), calc(100% - 48px)); margin: 0 auto; }}

    .topbar {{
      position: sticky; top: 0; z-index: 40;
      backdrop-filter: blur(12px);
      background: color-mix(in srgb, var(--bg) 84%, transparent);
      border-bottom: 1px solid var(--line);
    }}
    .topbar-inner {{
      min-height: 64px; display: flex; align-items: center;
      justify-content: space-between; gap: 16px;
    }}
    .brand-mini {{ display: flex; align-items: center; gap: 10px; }}
    .brand-dot {{
      width: 11px; height: 11px; border-radius: 999px;
      background: linear-gradient(135deg, var(--accent), var(--accent-2));
      box-shadow: 0 0 0 5px rgba(138,180,255,0.10); flex: 0 0 auto;
    }}
    .brand-mini strong {{ font-size: 0.95rem; letter-spacing: 0.01em; }}
    .toggle {{
      border: 1px solid var(--line); background: var(--bg-elev); color: var(--text);
      padding: 10px 14px; border-radius: 999px; cursor: pointer; font: inherit;
      transition: transform .15s ease, border-color .15s ease; white-space: nowrap;
    }}
    .toggle:hover {{ transform: translateY(-1px); border-color: color-mix(in srgb, var(--accent) 42%, var(--line)); }}

    /* Hero — all children inside .wrap for consistent alignment */
    header.hero {{ padding: 42px 0 0; }}
    .card-surface {{
      background: linear-gradient(180deg, color-mix(in srgb, var(--bg-elev) 94%, transparent), var(--bg-elev));
      border: 1px solid var(--line); border-radius: var(--radius); box-shadow: var(--shadow);
    }}
    .hero-grid {{ display: grid; grid-template-columns: 1.4fr 0.85fr; gap: 24px; }}
    .masthead {{ position: relative; overflow: hidden; padding: 28px 28px 24px; }}
    .masthead::after {{
      content: ""; position: absolute; right: -42px; bottom: -42px;
      width: 190px; height: 190px; border-radius: 999px;
      background: radial-gradient(circle, rgba(138,180,255,0.16), transparent 66%); pointer-events: none;
    }}
    .kicker {{
      display: inline-flex; align-items: center; gap: 8px; margin-bottom: 14px;
      color: var(--muted); text-transform: uppercase; letter-spacing: 0.16em;
      font-size: 0.72rem; font-weight: 800;
    }}
    .kicker::before {{ content: ""; width: 18px; height: 1px; background: var(--accent); display: inline-block; }}
    h1 {{ font-size: clamp(2.25rem, 5vw, 4rem); line-height: 0.96; letter-spacing: -0.045em; }}
    .tagline {{ margin: 14px 0 0; color: var(--muted); max-width: 58ch; font-size: 1.04rem; }}
    .issue-row {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 22px; }}
    .chip {{
      display: inline-flex; align-items: center; padding: 8px 12px; border-radius: 999px;
      border: 1px solid var(--line); background: var(--card); color: var(--muted); font-size: 0.9rem;
    }}
    .header-side {{ padding: 22px; display: flex; flex-direction: column; justify-content: space-between; gap: 18px; }}
    .header-side h2 {{ font-size: 0.86rem; text-transform: uppercase; letter-spacing: 0.15em; color: var(--soft); margin-bottom: 12px; }}
    .header-note {{ font-size: 1rem; }}
    .header-meta {{ border-top: 1px solid var(--line); padding-top: 14px; color: var(--muted); font-size: 0.94rem; }}

    /* Stats — inside .wrap, same gutter as hero-grid */
    .stats-row {{ display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 24px; margin-top: 24px; }}
    .stat-card {{ padding: 18px; }}
    .stat-label {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.13em; color: var(--soft); font-weight: 800; margin-bottom: 8px; }}
    .stat-value {{ font-size: clamp(1.55rem, 3vw, 2.2rem); font-weight: 800; letter-spacing: -0.04em; line-height: 1; color: var(--accent); }}
    .stat-value.sm {{ font-size: 1.2rem; padding-top: 4px; }}
    .stat-sub {{ font-size: 0.85rem; color: var(--muted); margin-top: 4px; }}

    /* Archive */
    main {{ padding: 36px 0 72px; }}
    .section-head {{ display: flex; align-items: baseline; justify-content: space-between; gap: 16px; margin-bottom: 16px; }}
    .section-head h2 {{ font-size: clamp(1.38rem, 2vw, 1.78rem); line-height: 1.12; letter-spacing: -0.02em; }}
    .section-head p {{ color: var(--muted); font-size: 0.95rem; }}
    .archive-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 16px; }}
    .issue-card {{
      background: linear-gradient(180deg, color-mix(in srgb, var(--bg-elev) 94%, transparent), var(--bg-elev));
      border: 1px solid var(--line); border-radius: var(--radius); box-shadow: var(--shadow);
      padding: 20px; display: flex; flex-direction: column; gap: 10px;
      text-decoration: none; transition: transform .15s ease, border-color .15s ease;
    }}
    .issue-card:hover {{ transform: translateY(-2px); border-color: color-mix(in srgb, var(--accent) 40%, var(--line)); text-decoration: none; }}
    .issue-card.latest {{ border-color: color-mix(in srgb, var(--accent) 55%, var(--line)); }}
    .card-top {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
    .issue-num {{ font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); }}
    .latest-badge {{
      font-size: 0.65rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em;
      padding: 4px 8px; border-radius: 999px;
      background: color-mix(in srgb, var(--accent) 18%, transparent);
      color: var(--accent); border: 1px solid color-mix(in srgb, var(--accent) 35%, transparent);
    }}
    .card-date {{ font-size: 0.88rem; color: var(--muted); }}
    .card-title {{ font-size: 1.02rem; font-weight: 700; color: var(--text); letter-spacing: -0.01em; line-height: 1.25; }}
    .card-preview {{ font-size: 0.88rem; color: var(--soft); line-height: 1.5; flex: 1; }}
    .card-arrow {{ font-size: 0.8rem; color: var(--accent); margin-top: 4px; }}
    .empty-state {{ grid-column: 1 / -1; text-align: center; padding: 4rem 2rem; color: var(--soft); }}
    .empty-state p {{ font-size: 1rem; max-width: 40ch; margin: 0 auto; }}

    footer {{ padding: 28px 0 44px; border-top: 1px solid var(--line); color: var(--muted); }}
    .footer-inner {{ display: flex; flex-wrap: wrap; justify-content: space-between; gap: 16px; align-items: end; }}
    .footer-inner strong {{ display: block; color: var(--text); margin-bottom: 4px; }}

    @media (max-width: 1080px) {{
      .hero-grid {{ grid-template-columns: 1fr 1fr; }}
      .archive-grid {{ grid-template-columns: 1fr 1fr; }}
      .stats-row {{ grid-template-columns: 1fr 1fr 1fr; }}
    }}
    @media (max-width: 760px) {{
      .wrap {{ width: min(var(--max), calc(100% - 24px)); }}
      .hero-grid, .archive-grid {{ grid-template-columns: 1fr; }}
      .stats-row {{ grid-template-columns: 1fr; }}
      .masthead, .header-side, .stat-card, .issue-card {{ padding: 16px; }}
      .topbar-inner {{ min-height: 58px; }}
    }}
  </style>
</head>
<body>

  <div class="topbar">
    <div class="wrap topbar-inner">
      <div class="brand-mini">
        <span class="brand-dot" aria-hidden="true"></span>
        <strong>The Dungeon Economy</strong>
      </div>
      <button class="toggle" id="themeToggle" type="button">Light mode</button>
    </div>
  </div>

  <header class="hero">
    <div class="wrap">
      <div class="hero-grid">
        <div class="masthead card-surface">
          <div class="kicker">Issue Archive</div>
          <h1>The Dungeon Economy</h1>
          <p class="tagline">A weekly brief on D&amp;D, publishing, platforms, and market signals.</p>
          <div class="issue-row">
            <span class="chip">Weekly</span>
            <span class="chip">D&amp;D · Publishing · Platforms · Demand</span>
          </div>
        </div>
        <aside class="header-side card-surface">
          <div>
            <h2>About this publication</h2>
            <p class="header-note">Each issue tracks what changed in D&amp;D and the wider tabletop market, separates confirmed fact from interpretation, and surfaces the signals that matter for players, DMs, and creators.</p>
          </div>
          <div class="header-meta">Where D&amp;D meets product, platform, and demand.</div>
        </aside>
      </div>

      <div class="stats-row">
        <div class="stat-card card-surface">
          <div class="stat-label">Issues published</div>
          <div class="stat-value">{total}</div>
          <div class="stat-sub">and counting</div>
        </div>
        <div class="stat-card card-surface">
          <div class="stat-label">Focus</div>
          <div class="stat-value sm">D&amp;D + Industry</div>
          <div class="stat-sub">WotC-first, market-wide</div>
        </div>
        <div class="stat-card card-surface">
          <div class="stat-label">Cadence</div>
          <div class="stat-value sm">Weekly</div>
          <div class="stat-sub">Published every Friday</div>
        </div>
      </div>
    </div>
  </header>

  <main>
    <div class="wrap">
      <div class="section-head">
        <h2>All Issues</h2>
        <p>Most recent first.</p>
      </div>
      <div class="archive-grid">
        {cards_html}
      </div>
    </div>
  </main>

  <footer>
    <div class="wrap footer-inner">
      <div>
        <strong>The Dungeon Economy</strong>
        <div>Weekly intelligence brief</div>
      </div>
      <div>Where D&amp;D meets product, platform, and demand.</div>
    </div>
  </footer>

  <script>
    (function () {{
      const key = 'dungeon-economy-theme';
      const root = document.documentElement;
      const btn = document.getElementById('themeToggle');
      function apply(theme) {{
        root.setAttribute('data-theme', theme);
        btn.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
      }}
      const saved = localStorage.getItem(key);
      apply(saved === 'light' || saved === 'dark' ? saved : 'dark');
      btn.addEventListener('click', function () {{
        const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        localStorage.setItem(key, next);
        apply(next);
      }});
    }})();
  </script>
</body>
</html>"""

Path("index.html").write_text(index_html, encoding="utf-8")
print(f"index.html rebuilt — {total} issue(s) listed.")
