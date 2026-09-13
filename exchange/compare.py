"""One view of everyone's process logs and skills, focused on what each person typed.

    python compare.py [EXCHANGE_DIR]      # writes COMPARISON.md and COMPARISON.html into EXCHANGE_DIR

Reads EXCHANGE_DIR/logs/<name>/* and EXCHANGE_DIR/skills/<name>/*. Each log becomes a list of
(user input, Claude's reply) pairs. Formats: Claude Code session .jsonl; share.py output
("> " user lines, "⏺ " assistant lines); "User:"/"Human:" transcripts; anything else is kept as notes.
"""
import json, re, html, statistics, sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
SKIP = ("<", "Base directory for this skill", "Approach this as the design lead")
CHECK_WORDS = re.compile(r"\b(check|verify|verif|test|sanity|control|baseline|ood|shuffle|confound)\w*", re.I)
REPLY_CAP = 6000

def _text(content):
    if isinstance(content, str): return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return ""

def pairs_jsonl(p):
    pairs = []
    for line in p.read_text(errors="replace").splitlines():
        try: d = json.loads(line)
        except Exception: continue
        if d.get("isMeta"): continue
        t = _text(d.get("message", {}).get("content")).strip()
        if not t: continue
        if d.get("type") == "user":
            if not t.startswith(SKIP): pairs.append([t, ""])
        elif d.get("type") == "assistant" and pairs:
            pairs[-1][1] = (pairs[-1][1] + "\n\n" + t).strip()[:REPLY_CAP]
    return [tuple(x) for x in pairs]

def pairs_text(p):
    txt = p.read_text(errors="replace")
    pairs = []
    if re.search(r"^> ", txt, re.M):
        mode = None
        for line in txt.splitlines():
            if line.startswith("> "):
                if mode != "u": pairs.append([line[2:], ""]); mode = "u"
                else: pairs[-1][0] += "\n" + line[2:]
            elif line.startswith("⏺ ") and pairs:
                pairs[-1][1] += ("\n" if pairs[-1][1] else "") + line[2:]; mode = "a"
            elif line.strip() == "": mode = None if mode == "u" else mode
            elif mode == "a" and pairs: pairs[-1][1] += "\n" + line
    elif re.search(r"^(User|Human):", txt, re.M):
        for m in re.finditer(r"^(?:User|Human):\s*(.*?)(?:^(?:Assistant|AI|Claude):\s*(.*?))?(?=^(?:User|Human):|\Z)", txt, re.S | re.M):
            u = (m.group(1) or "").strip(); a = (m.group(2) or "").strip()
            if u: pairs.append([u, a[:REPLY_CAP]])
    return [(u.strip(), a.strip()) for u, a in pairs if u.strip()]

def load_person(name):
    logs, notes = [], []
    ldir = ROOT / "logs" / name
    for p in (sorted(ldir.glob("*")) if ldir.exists() else []):
        if p.name.lower().startswith("notes") or p.suffix.lower() in (".png", ".jpg"): continue
        pr = pairs_jsonl(p) if p.suffix == ".jsonl" else pairs_text(p)
        if pr: logs.append((p.name, pr))
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
    turns = [u for _, pr in person["logs"] for u, _ in pr]
    if not turns: return {"n": 0, "median_words": 0, "checks": 0, "questions": 0}
    words = [len(t.split()) for t in turns]
    return {"n": len(turns), "median_words": int(statistics.median(words)),
            "checks": sum(bool(CHECK_WORDS.search(t)) for t in turns), "questions": sum("?" in t for t in turns)}

def main():
    names = sorted({d.name for sub in ("logs", "skills") if (ROOT / sub).exists() for d in (ROOT / sub).iterdir() if d.is_dir()})
    people = [load_person(n) for n in names]
    md = ["# Comparison: what each person typed, and what they've made reusable", "",
          "| Person | Prompts | Median words / prompt | Prompts mentioning a check | Questions asked | Skills shared |", "|---|---|---|---|---|---|"]
    for p in people:
        s = stats(p)
        md.append(f"| {p['name']} | {s['n']} | {s['median_words']} | {s['checks']} | {s['questions']} | {len(p['skills'])} |")
    for p in people:
        md += ["", f"## {p['name']}", ""]
        if p["skills"]:
            md += ["**Skills shared**", *[f"- `{n}` — {d}" for n, d in p["skills"]], ""]
        for fname, pr in p["logs"]:
            md.append(f"**User input, in order** (`{fname}`); Claude's reply indented under each")
            for i, (u, a) in enumerate(pr, 1):
                md.append(f"{i}. {u.replace(chr(10), ' ')[:300]}")
                if a: md.append(f"   > {a.replace(chr(10), ' ')[:300]}")
            md.append("")
        for fname, body in p["notes"]:
            md += [f"**Notes** (`{fname}`)", "", "```", body.strip()[:800], "```", ""]
    (ROOT / "COMPARISON.md").write_text("\n".join(md))

    cols = []
    for p in people:
        s = stats(p)
        sk = "".join(f"<li><code>{html.escape(n)}</code> {html.escape(d)}</li>" for n, d in p["skills"]) or "<li class=m>none yet</li>"
        items = []
        for _, pr in p["logs"]:
            for u, a in pr:
                cls = " class=chk" if CHECK_WORDS.search(u) else ""
                reply = f"<details><summary>Claude's reply · {len(a.split())} words</summary><pre>{html.escape(a)}</pre></details>" if a else "<p class=m>no text reply captured</p>"
                items.append(f"<li{cls}><div class=u>{html.escape(u)}</div>{reply}</li>")
        pr_html = "".join(items) or "<li class=m>no log yet</li>"
        cols.append(f"<section><h2>{html.escape(p['name'])}</h2><p class=m>{s['n']} prompts · median {s['median_words']} words · {s['checks']} mention a check</p>"
                    f"<h3>Skills</h3><ul class=sk>{sk}</ul><h3>User input, in order</h3><ol class=pr>{pr_html}</ol></section>")
    page = f"""<!doctype html><meta charset=utf-8><title>Exchange comparison</title>
<style>body{{margin:0;padding:20px;box-sizing:border-box;max-width:100vw;overflow-x:hidden;font:14px/1.45 system-ui,sans-serif;color:#1b1f1a;background:#f5f6f2}}
h1{{font-size:20px;margin:0 0 4px}}p.lede{{margin:0 0 16px;color:#4e564f}}.m{{color:#7a827b;margin:2px 0 0;font-size:12px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(360px,100%),1fr));gap:14px;align-items:start}}
section{{min-width:0;background:#fff;border:1px solid #d6dad3;border-radius:4px;padding:12px 14px;max-height:88vh;overflow-y:auto}}
h2{{font-size:17px;margin:0}}h3{{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#7a827b;margin:12px 0 4px}}
ul,ol{{margin:0;padding-left:20px}}li{{margin-bottom:8px;word-break:break-word}}
.pr li{{border-left:3px solid #e6e9e3;padding-left:8px}}.pr li.chk{{border-left-color:#1f5e3f}}
.u{{white-space:pre-wrap}}details{{margin-top:4px}}summary{{cursor:pointer;color:#1f5e3f;font-size:12.5px;font-weight:600}}
details pre{{white-space:pre-wrap;font:12px/1.45 ui-monospace,monospace;background:#f0f2ec;padding:8px;border-radius:3px;margin:4px 0 0;max-height:320px;overflow:auto}}
code{{background:#f0f2ec;padding:1px 4px;border-radius:3px}}
@media(prefers-color-scheme:dark){{body{{background:#141715;color:#e6e9e3}}section{{background:#1d211e;border-color:#2e3430}}code,details pre{{background:#171b18}}.pr li{{border-left-color:#2e3430}}.pr li.chk{{border-left-color:#6fbf8e}}summary{{color:#6fbf8e}}}}</style>
<h1>Exchange comparison</h1><p class=lede>One column per person. Green bar = the prompt mentions a check, test, control or baseline. Open "Claude's reply" under any prompt. Regenerate with <code>python exchange/compare.py</code>.</p>
<div class=grid>{''.join(cols)}</div>"""
    (ROOT / "COMPARISON.html").write_text(page)
    (ROOT / "index.html").write_text(page)   # so a static host serves it at /
    print(f"{len(people)} people → {ROOT/'COMPARISON.md'}, {ROOT/'COMPARISON.html'}")

if __name__ == "__main__":
    main()
