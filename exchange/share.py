"""Share your session's user input and your skills to the exchange, in one command.

    uv run python exchange/share.py <your-name> [--session latest|<path.jsonl>] [--push]

What it does:
  1. Finds your most recent Claude Code session for this project (~/.claude/projects/<cwd-slug>/*.jsonl)
     and writes ONLY the user turns (what you typed) to exchange/logs/<name>/<date>-session.md.
     Assistant output, tool results and file contents are not copied. Review the file before pushing.
  2. Copies every SKILL.md under this project's .claude/skills/ to exchange/skills/<name>/.
  3. Regenerates exchange/COMPARISON.md and .html.
  4. With --push: git add, commit, push.
"""
import argparse, datetime, json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
SKIP = ("<", "Base directory for this skill", "Approach this as the design lead")

def latest_session():
    """Most recent session whose cwd was this project or a parent of it."""
    cands = []
    for base in [PROJECT, *PROJECT.parents]:
        d = Path.home() / ".claude" / "projects" / ("-" + str(base).strip("/").replace("/", "-"))
        if d.exists(): cands += list(d.glob("*.jsonl"))
    cands.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None

def user_turns(p):
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name"); ap.add_argument("--session", default="latest"); ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    name = re.sub(r"[^a-z0-9-]", "-", a.name.lower())
    logdir, skdir = ROOT / "logs" / name, ROOT / "skills" / name
    logdir.mkdir(parents=True, exist_ok=True); skdir.mkdir(parents=True, exist_ok=True)

    sess = latest_session() if a.session == "latest" else Path(a.session)
    if sess and sess.exists():
        turns = user_turns(sess)
        out = logdir / f"{datetime.date.today()}-session.md"
        out.write_text(f"# {name} — user input from session {sess.stem[:8]}\n\n" + "\n\n".join("> " + t.replace("\n", "\n> ") for t in turns) + "\n")
        print(f"wrote {out.relative_to(PROJECT)} ({len(turns)} user turns). Review it before pushing.")
    else:
        print("no session found; skipping log")

    n = 0
    for sk in (PROJECT / ".claude" / "skills").glob("*/SKILL.md"):
        shutil.copy(sk, skdir / f"{sk.parent.name}.SKILL.md"); n += 1
    print(f"copied {n} skill(s) to {skdir.relative_to(PROJECT)}")

    subprocess.run([sys.executable, str(ROOT / "compare.py")], check=False)
    if a.push:
        subprocess.run(["git", "add", "exchange"], cwd=PROJECT, check=True)
        subprocess.run(["git", "commit", "-m", f"exchange: {name} shares session input and skills"], cwd=PROJECT, check=False)
        subprocess.run(["git", "push"], cwd=PROJECT, check=False)

if __name__ == "__main__":
    main()
