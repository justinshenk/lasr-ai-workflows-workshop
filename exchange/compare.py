"""One view of everyone's process logs and skills, focused on what each person typed.

    uv run python exchange/compare.py          # writes exchange/COMPARISON.md and COMPARISON.html

Reads exchange/logs/<name>/* and exchange/skills/<name>/*.
Log formats: Claude Code session .jsonl (user turns), Claude Code /export text ("> " lines),
"User:"/"Human:" transcripts, or anything else (kept whole as notes).
"""
import json, re, html, statistics
from pathlib import Path

ROOT = Path(__file__).parent
SKIP = ("<", "Base directory for this skill", "Approach this as the design lead")
CHECK_WORDS = re.compile(r"\b(check|verify|verif|test|sanity|control|baseline|ood|shuffle|confound)\w*", re.I)

def user_turns_jsonl(p):
    out = []
    for line in p.read_text(errors="replace").splitlines():
        try: d = json.loads(line)
        except Exception: continue
        if d.get("type") != "user" or d.get("isMeta"): continue
        c = d.get("message", {}).get("content")
        if isinstance(c, str): t = c
        elif isinstance(c, list): t = "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
        else: t = ""
        t = t.strip()
        if t and not t.startswith(SKIP): out.append(t)
    return out

def user_turns_text(p):
    txt = p.read_text(errors="replace")
    turns, cur = [], []
    if re.search(r"^> ", txt, re.M):                      # Claude Code /export style, or share.py output
        for line in txt.splitlines():
            if line.startswith("> "): cur.append(line[2:])
            elif cur and line.strip() == "": turns.append("\n".join(cur).strip()); cur = []
            elif cur and not line.startswith(("⏺", "  ")): turns.append("\n".join(cur).strip()); cur = []
        if cur: turns.append("\n".join(cur).strip())
    elif re.search(r"^(User|Human):", txt, re.M):
        for m in re.finditer(r"^(?:User|Human):\s*(.*?)(?=^(?:User|Human|Assistant|AI|Claude):|\Z)", txt, re.S | re.M):
            t = m.group(1).strip()
            if t: turns.append(t)
    return [t for t in turns if t]

def load_person(name):
    logs, notes = [], []
    ldir = ROOT / "logs" / name
    for p in sorted(ldir.glob("*")) if ldir.exists() else []:
        if p.name.lower().startswith("notes") or p.suffix.lower() in (".png", ".jpg"): continue
        turns = user_turns_jsonl(p) if p.suffix == ".jsonl" else user_turns_text(p)
        if turns: logs.append((p.name, turns))
        else: notes.append((p.name, p.read_text(errors="replace")[:1500]))
    skills = []
    sdir = ROOT / "skills" / name
    if sdir.exists():
        for p in sorted(sdir.glob("*")):
            if p.is_file():
                body = p.read_text(errors="replace")
                m = re.search(r"^description:\s*(.+)$", body, re.M)
                first = body.strip().splitlines()[0] if body.strip() else ""
                skills.append((p.name, (m.group(1) if m else first).strip()[:160]))
    return {"name": name, "logs": logs, "notes": notes, "skills": skills}

def stats(person):
    turns = [t for _, ts in person["logs"] for t in ts]
    if not turns: return {"n": 0, "median_words": 0, "checks": 0, "questions": 0}
    words = [len(t.split()) for t in turns]
    return {"n": len(turns), "median_words": int(statistics.median(words)),
            "checks": sum(bool(CHECK_WORDS.search(t)) for t in turns),
            "questions": sum("?" in t for t in turns)}

def main():
    names = sorted({d.name for sub in ("logs", "skills") if (ROOT / sub).exists()
                    for d in (ROOT / sub).iterdir() if d.is_dir()})
    people = [load_person(n) for n in names]
    # ---- Markdown ----
    md = ["# Comparison: what each person typed, and what they've made reusable", "",
          "| Person | Prompts | Median words / prompt | Prompts mentioning a check | Questions asked | Skills shared |",
          "|---|---|---|---|---|---|"]
    for p in people:
        s = stats(p)
        md.append(f"| {p['name']} | {s['n']} | {s['median_words']} | {s['checks']} | {s['questions']} | {len(p['skills'])} |")
    for p in people:
        md += ["", f"## {p['name']}", ""]
        if p["skills"]:
            md.append("**Skills shared**")
            md += [f"- `{n}` — {d}" for n, d in p["skills"]]
            md.append("")
        for fname, turns in p["logs"]:
            md.append(f"**User input, in order** (`{fname}`)")
            md += [f"{i}. {t.replace(chr(10), ' ')[:300]}" for i, t in enumerate(turns, 1)]
            md.append("")
        for fname, body in p["notes"]:
            md += [f"**Notes** (`{fname}`)", "", "```", body.strip()[:800], "```", ""]
    (ROOT / "COMPARISON.md").write_text("\n".join(md))
    # ---- HTML: one column per person ----
    cols = []
    for p in people:
        s = stats(p)
        sk = "".join(f"<li><code>{html.escape(n)}</code> {html.escape(d)}</li>" for n, d in p["skills"]) or "<li class=m>none yet</li>"
        turns = [t for _, ts in p["logs"] for t in ts]
        pr = "".join(f"<li{' class=chk' if CHECK_WORDS.search(t) else ''}>{html.escape(t)}</li>" for t in turns) or "<li class=m>no log yet</li>"
        cols.append(f"<section><h2>{html.escape(p['name'])}</h2><p class=m>{s['n']} prompts · median {s['median_words']} words · {s['checks']} mention a check</p>"
                    f"<h3>Skills</h3><ul class=sk>{sk}</ul><h3>User input, in order</h3><ol class=pr>{pr}</ol></section>")
    page = f"""<!doctype html><meta charset=utf-8><title>Exchange comparison</title>
<style>body{{margin:0;padding:20px;font:14px/1.45 system-ui,sans-serif;color:#1b1f1a;background:#f5f6f2}}
h1{{font-size:20px;margin:0 0 4px}}p.lede{{margin:0 0 16px;color:#4e564f}}.m{{color:#7a827b}}
.grid{{display:flex;gap:14px;overflow-x:auto;align-items:flex-start}}
section{{flex:0 0 360px;background:#fff;border:1px solid #d6dad3;border-radius:4px;padding:12px 14px;max-height:85vh;overflow-y:auto}}
h2{{font-size:17px;margin:0}}h3{{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#7a827b;margin:12px 0 4px}}
ul,ol{{margin:0;padding-left:20px}}li{{margin-bottom:6px;white-space:pre-wrap;word-break:break-word}}
.pr li{{border-left:3px solid #e6e9e3;padding-left:8px}}.pr li.chk{{border-left-color:#1f5e3f}}
code{{background:#f0f2ec;padding:1px 4px;border-radius:3px}}
@media(prefers-color-scheme:dark){{body{{background:#141715;color:#e6e9e3}}section{{background:#1d211e;border-color:#2e3430}}code{{background:#171b18}}.pr li{{border-left-color:#2e3430}}.pr li.chk{{border-left-color:#6fbf8e}}}}</style>
<h1>Exchange comparison</h1><p class=lede>One column per person. Green bar = the prompt mentions a check, test, control or baseline. Regenerate with <code>uv run python exchange/compare.py</code>.</p>
<div class=grid>{''.join(cols)}</div>"""
    (ROOT / "COMPARISON.html").write_text(page)
    print(f"{len(people)} people → exchange/COMPARISON.md, exchange/COMPARISON.html")

if __name__ == "__main__":
    main()
