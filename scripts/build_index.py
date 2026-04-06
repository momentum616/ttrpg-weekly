"""
build_index.py
1. Scans /reports for HTML files (sorted by filename date, newest first)
2. Injects working prev/next navigation into each report's topbar
3. Rebuilds index.html as the archive homepage

Run this script from the repo root after adding a new report to /reports/.
"""

import re
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path("reports")

# ── Gather all reports ────────────────────────────────────────────────────────

reports = sorted(REPORTS_DIR.glob("*.html"), key=lambda p: p.stem)  # oldest → newest
total = len(reports)

def slug_to_display(slug):
    """2026-04-04 → April 4, 2026"""
    try:
        return datetime.strptime(slug, "%Y-%m-%d").strftime("%B %d, %Y")
    except ValueError:
        return slug

def extract_meta(path):
    """Pull issue number and first meaningful h2 headline from the HTML."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    issue_match = re.search(r'Issue\s*#(\d+)', text)
    issue = int(issue_match.group(1)) if issue_match else "—"
    headlines = re.findall(r'<h2[^>]*>(.*?)</h2>', text, re.DOTALL)
    headlines = [re.sub(r'<[^>]+>', '', h).strip() for h in headlines if len(h.strip()) > 10]
    preview = headlines[0] if headlines else "Weekly TTRPG intelligence report"
    return issue, preview[:120]

# ── Inject prev/next nav into each report ────────────────────────────────────

def make_nav_btn(slug, label, arrow_left=False):
    arrow = "&#8592; " if arrow_left else ""
    arrow_r = " &#8594;" if not arrow_left else ""
    return f'<a href="../reports/{slug}.html" class="nav-btn">{arrow}{label}{arrow_r}</a>'

def disabled_btn(label, arrow_left=False):
    arrow = "&#8592; " if arrow_left else ""
    arrow_r = " &#8594;" if not arrow_left else ""
    return f'<a href="#" class="nav-btn disabled">{arrow}{label}{arrow_r}</a>'

for i, path in enumerate(reports):
    text = path.read_text(encoding="utf-8", errors="ignore")

    prev_path = reports[i - 1] if i > 0 else None
    next_path = reports[i + 1] if i < len(reports) - 1 else None

    prev_btn = make_nav_btn(prev_path.stem, "Previous", arrow_left=True) if prev_path else disabled_btn("Previous", arrow_left=True)
    next_btn = make_nav_btn(next_path.stem, "Next") if next_path else disabled_btn("Next")

    # Replace the two nav-btn anchors in the topbar-right div
    # Matches both enabled and disabled variants
    nav_pattern = re.compile(
        r'(<div class="topbar-right">.*?)'          # open topbar-right
        r'<a[^>]*class="nav-btn[^"]*"[^>]*>.*?</a>' # prev btn
        r'(\s*<span[^>]*></span>\s*)?'               # optional divider span
        r'<a[^>]*class="nav-btn[^"]*"[^>]*>.*?</a>' # next btn
        r'(.*?</div>)',                               # rest of topbar-right
        re.DOTALL
    )

    divider = '\n      <span class="nav-divider"></span>\n      '

    def replacer(m):
        return f'{m.group(1)}{prev_btn}{divider}{next_btn}{m.group(3)}'

    new_text, count = nav_pattern.subn(replacer, text, count=1)

    if count == 0:
        print(f"  WARNING: Could not find nav buttons in {path.name} — skipping nav injection")
    else:
        path.write_text(new_text, encoding="utf-8")
        prev_label = prev_path.stem if prev_path else "none"
        next_label = next_path.stem if next_path else "none"
        print(f"  ✓ {path.name}  ←{prev_label}  →{next_label}")

print(f"\nNav injection complete for {total} report(s).")

# ── Build cards HTML ──────────────────────────────────────────────────────────

cards_html = ""
for i, path in enumerate(reversed(reports)):  # newest first for display
    slug        = path.stem
    display     = slug_to_display(slug)
    issue, preview = extract_meta(path)
    is_latest   = i == 0
    border_style = "border:2px solid var(--accent);" if is_latest else "border:1px solid var(--line);"
    badge       = '<span class="badge">Latest</span>' if is_latest else ""

    cards_html += f"""
    <a href="reports/{slug}.html" class="card">
      <div class="card-inner" style="{border_style}">
        <div class="card-top">
          <span class="issue-label">Issue #{issue}</span>
          {badge}
        </div>
        <div class="card-date">{display}</div>
        <div class="card-preview">{preview}…</div>
      </div>
    </a>"""

# ── Write index.html ──────────────────────────────────────────────────────────

index_html = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Dungeon Economy — Archive</title>
  <style>
    :root {{
      --bg:#0c0f14; --bg-elev:#121722; --bg-soft:#151b26;
      --card:rgba(255,255,255,0.04); --line:rgba(255,255,255,0.10);
      --text:#edf2f8; --muted:#aeb8ca; --soft:#8e98ab;
      --accent:#8ab4ff; --accent-2:#93f0c8; --warn:#ffcf78;
    }}
    html[data-theme="light"] {{
      --bg:#f4eee4; --bg-elev:#fbf7ef; --bg-soft:#ede7d8;
      --line:rgba(0,0,0,0.10); --card:rgba(0,0,0,0.03);
      --text:#211a14; --muted:#5a5248; --soft:#7a706a;
      --accent:#245dc5; --accent-2:#0a8b69; --warn:#9a6700;
    }}
    *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
    body {{ font-family:system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--text); min-height:100vh; padding:2rem 1rem; }}
    .wrap {{ max-width:800px; margin:0 auto; }}
    header {{ border-bottom:1px solid var(--line); padding-bottom:1.5rem; margin-bottom:2rem; display:flex; justify-content:space-between; align-items:flex-end; }}
    header h1 {{ font-size:22px; font-weight:700; color:var(--text); }}
    header p {{ font-size:13px; color:var(--muted); margin-top:4px; }}
    .toggle {{ background:var(--bg-elev); border:1px solid var(--line); color:var(--muted); font-size:0.75rem; font-weight:600; padding:6px 12px; border-radius:999px; cursor:pointer; }}
    .stats {{ display:flex; gap:12px; margin-bottom:2rem; flex-wrap:wrap; }}
    .stat {{ background:var(--bg-elev); border:1px solid var(--line); border-radius:8px; padding:12px 16px; flex:1; min-width:100px; }}
    .stat-label {{ font-size:10px; text-transform:uppercase; letter-spacing:0.07em; color:var(--soft); margin-bottom:4px; }}
    .stat-value {{ font-size:20px; font-weight:700; color:var(--text); }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:12px; }}
    .card {{ text-decoration:none; color:inherit; display:block; }}
    .card-inner {{ border-radius:10px; padding:18px 20px; background:var(--bg-elev); transition:box-shadow .15s; }}
    .card-inner:hover {{ box-shadow:0 0 0 2px var(--accent); }}
    .card-top {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }}
    .issue-label {{ font-size:11px; font-weight:700; color:var(--accent); text-transform:uppercase; letter-spacing:0.06em; }}
    .badge {{ background:color-mix(in srgb,var(--accent) 15%,transparent); color:var(--accent); font-size:10px; font-weight:700; padding:2px 8px; border-radius:999px; border:1px solid color-mix(in srgb,var(--accent) 30%,transparent); }}
    .card-date {{ font-size:14px; font-weight:600; color:var(--text); margin-bottom:6px; }}
    .card-preview {{ font-size:13px; color:var(--muted); line-height:1.5; }}
    footer {{ margin-top:3rem; padding-top:1.5rem; border-top:1px solid var(--line); font-size:12px; color:var(--soft); text-align:center; }}
    .brand-dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; background:var(--accent); margin-right:6px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <div>
        <h1><span class="brand-dot"></span>The Dungeon Economy</h1>
        <p>Weekly intelligence brief &nbsp;·&nbsp; D&D, publishing, platforms &amp; market signals</p>
      </div>
      <button class="toggle" id="themeToggle">Light mode</button>
    </header>

    <div class="stats">
      <div class="stat">
        <div class="stat-label">Issues published</div>
        <div class="stat-value">{total}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Focus</div>
        <div class="stat-value" style="font-size:14px;padding-top:3px;">D&amp;D + Industry</div>
      </div>
      <div class="stat">
        <div class="stat-label">Cadence</div>
        <div class="stat-value" style="font-size:14px;padding-top:3px;">Weekly</div>
      </div>
    </div>

    <div class="grid">
      {cards_html}
    </div>

    <footer>
      The Dungeon Economy &nbsp;·&nbsp; Where D&amp;D meets product, platform, and demand
    </footer>
  </div>

  <script>
    const key='dungeon-economy-theme',root=document.documentElement,btn=document.getElementById('themeToggle');
    function apply(t){{root.setAttribute('data-theme',t);btn.textContent=t==='dark'?'Light mode':'Dark mode';}}
    const saved=localStorage.getItem(key);
    apply(saved==='light'||saved==='dark'?saved:'dark');
    btn.addEventListener('click',function(){{const next=root.getAttribute('data-theme')==='dark'?'light':'dark';localStorage.setItem(key,next);apply(next);}});
  </script>
</body>
</html>"""

Path("index.html").write_text(index_html, encoding="utf-8")
print(f"index.html rebuilt — {total} report(s) listed.")
