"""
build_index.py
Scans /reports for HTML files and regenerates index.html.
Triggered automatically by GitHub Actions when a new report is pushed.
"""

import re
from pathlib import Path
from datetime import datetime

REPORTS_DIR = Path("reports")

reports = sorted(REPORTS_DIR.glob("*.html"), reverse=True)

def slug_to_display(slug):
    try:
        return datetime.strptime(slug, "%Y-%m-%d").strftime("%B %d, %Y")
    except ValueError:
        return slug

def extract_meta(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    issue_match = re.search(r'Issue\s*#(\d+)', text)
    issue = issue_match.group(1) if issue_match else "—"
    headlines = re.findall(r'<h[23][^>]*>(.*?)</h[23]>', text, re.DOTALL)
    headlines = [re.sub(r'<[^>]+>', '', h).strip() for h in headlines if len(h.strip()) > 20]
    preview = headlines[0] if headlines else "Weekly TTRPG intelligence report"
    return issue, preview[:120]

cards_html = ""
for i, path in enumerate(reports):
    slug        = path.stem
    display     = slug_to_display(slug)
    issue, preview = extract_meta(path)
    is_latest   = i == 0
    border      = "border: 2px solid #7F77DD;" if is_latest else "border: 1px solid #e8e6e0;"
    badge       = '<span style="background:#EEEDFE;color:#3C3489;font-size:11px;font-weight:600;padding:3px 10px;border-radius:6px;margin-left:8px;">Latest</span>' if is_latest else ""

    cards_html += f"""
    <a href="reports/{slug}.html" style="text-decoration:none;color:inherit;">
      <div style="{border}border-radius:10px;padding:18px 20px;background:#fff;cursor:pointer;"
           onmouseover="this.style.boxShadow='0 2px 12px rgba(0,0,0,0.07)'"
           onmouseout="this.style.boxShadow='none'">
        <div style="display:flex;align-items:center;margin-bottom:6px;">
          <span style="font-size:12px;font-weight:600;color:#7F77DD;">Issue #{issue}</span>
          {badge}
        </div>
        <div style="font-size:15px;font-weight:500;color:#1a1a18;margin-bottom:5px;">{display}</div>
        <div style="font-size:13px;color:#5a5a56;line-height:1.5;">{preview}…</div>
      </div>
    </a>"""

total = len(reports)

index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TTRPG Weekly Intelligence</title>
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}
    body{{font-family:system-ui,-apple-system,sans-serif;background:#f8f8f6;color:#1a1a18;padding:2rem 1rem;min-height:100vh;}}
    .wrap{{max-width:720px;margin:0 auto;}}
    header{{border-bottom:1px solid #e8e6e0;padding-bottom:1.5rem;margin-bottom:2rem;}}
    header h1{{font-size:24px;font-weight:600;margin-bottom:4px;}}
    header p{{font-size:14px;color:#5a5a56;}}
    .stats{{display:flex;gap:12px;margin-bottom:2rem;flex-wrap:wrap;}}
    .stat{{background:#fff;border:1px solid #e8e6e0;border-radius:8px;padding:12px 16px;flex:1;min-width:120px;}}
    .stat-label{{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:#888;margin-bottom:4px;}}
    .stat-value{{font-size:20px;font-weight:600;}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px;}}
    .empty{{text-align:center;padding:3rem;color:#aaa;font-size:14px;}}
    footer{{margin-top:3rem;padding-top:1.5rem;border-top:1px solid #e8e6e0;font-size:12px;color:#aaa;text-align:center;}}
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>TTRPG Weekly Intelligence</h1>
      <p>D&amp;D-focused · Industry-wide · Published weekly</p>
    </header>
    <div class="stats">
      <div class="stat"><div class="stat-label">Total issues</div><div class="stat-value">{total}</div></div>
      <div class="stat"><div class="stat-label">Focus</div><div class="stat-value" style="font-size:14px;padding-top:3px;">D&amp;D + Industry</div></div>
      <div class="stat"><div class="stat-label">Cadence</div><div class="stat-value" style="font-size:14px;padding-top:3px;">Weekly</div></div>
    </div>
    {"<div class='grid'>" + cards_html + "</div>" if reports else "<div class='empty'>No reports yet. Drop your first HTML file into /reports to get started.</div>"}
    <footer>Powered by Claude &nbsp;·&nbsp; Sources: EN World · TTRPG Insider · Dicebreaker · Reddit · Kickstarter</footer>
  </div>
</body>
</html>"""

Path("index.html").write_text(index_html, encoding="utf-8")
print(f"index.html rebuilt — {total} report(s) listed.")
