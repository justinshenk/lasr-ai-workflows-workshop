"""Post what you typed in your latest Claude Code session, plus your project's skills, to the cohort exchange.

    python share.py <your-name> --list                       # show what WOULD be shared; writes nothing
    python share.py <your-name> [--skills all|none|a,b] [--no-log] [--project DIR] [--exchange DIR]
                                [--repo URL] [--session latest|PATH] [--push]

Defaults: --project = current directory; --exchange = ~/lasr-exchange (cloned from --repo or
$LASR_EXCHANGE_REPO if missing). Writes ONLY user turns: no assistant output, tool results or file contents.
"""
import argparse, datetime, json, os, re, shutil, subprocess, sys
from pathlib import Path

SKIP = ("<", "Base directory for this skill", "Approach this as the design lead")

def latest_session(project: Path):
    cands = []
    for base in [project, *project.parents]:
        d = Path.home() / ".claude" / "projects" / ("-" + str(base).strip("/").replace("/", "-"))
        if d.exists(): cands += list(d.glob("*.jsonl"))
    cands.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None

REPLY_CAP = 6000

def _text(c):
    if isinstance(c, str): return c
    if isinstance(c, list): return "\n".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text")
    return ""

def turn_pairs(p: Path):
    """[(what the user typed, Claude's text reply)] — text only; no tool calls, tool results or file contents."""
    pairs = []
    for line in p.read_text(errors="replace").splitlines():
        try: d = json.loads(line)
        except Exception: continue
        if d.get("isMeta"): continue
        if d.get("type") == "attachment":                       # a message the user typed mid-turn
            att = d.get("attachment") or {}
            if att.get("type") == "queued_command" and att.get("prompt", "").strip():
                pairs.append([att["prompt"].strip(), ""])
            continue
        t = _text(d.get("message", {}).get("content")).strip()
        if not t: continue
        if d.get("type") == "user":
            if not t.startswith(SKIP): pairs.append([t, ""])
        elif d.get("type") == "assistant" and pairs:
            pairs[-1][1] = (pairs[-1][1] + "\n\n" + t).strip()[:REPLY_CAP]
    return pairs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--project", default=os.getcwd())
    ap.add_argument("--exchange", default=os.environ.get("LASR_EXCHANGE_DIR", str(Path.home() / "lasr-exchange")))
    ap.add_argument("--repo", default=os.environ.get("LASR_EXCHANGE_REPO", ""))
    ap.add_argument("--session", default="latest")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--list", action="store_true", help="print the session summary and skills found, write nothing")
    ap.add_argument("--skills", default="all", help="all | none | comma-separated skill names to share")
    ap.add_argument("--no-log", action="store_true", help="share skills only, not the session")
    a = ap.parse_args()

    project, exchange = Path(a.project).resolve(), Path(a.exchange).expanduser().resolve()
    found = sorted((project / ".claude" / "skills").glob("*/SKILL.md"))
    if a.list:
        sess = latest_session(project) if a.session == "latest" else Path(a.session)
        if sess and sess.exists():
            pairs = turn_pairs(sess)
            print(f"SESSION {sess} — {len(pairs)} user turns")
            for i, (u, _) in enumerate(pairs, 1): print(f"  {i}. {u.splitlines()[0][:100]}")
        else: print("SESSION none found for this project")
        print(f"SKILLS found in {project / '.claude/skills'}: {len(found)}")
        for sk in found:
            m = re.search(r"^description:\s*(.+)$", sk.read_text(errors="replace"), re.M)
            print(f"  - {sk.parent.name}: {(m.group(1) if m else '').strip()[:100]}")
        return
    if a.skills == "none": chosen = []
    elif a.skills == "all": chosen = found
    else:
        want = {x.strip() for x in a.skills.split(",") if x.strip()}
        chosen = [sk for sk in found if sk.parent.name in want]
        missing = want - {sk.parent.name for sk in chosen}
        if missing: sys.exit(f"skills not found in this project: {', '.join(sorted(missing))}")
    if not exchange.exists():
        if not a.repo: sys.exit(f"{exchange} not found and no --repo / $LASR_EXCHANGE_REPO to clone from.")
        subprocess.run(["git", "clone", a.repo, str(exchange)], check=True)
    root = exchange / "exchange" if (exchange / "exchange").exists() else exchange
    name = re.sub(r"[^a-z0-9-]", "-", a.name.lower())
    logdir, skdir = root / "logs" / name, root / "skills" / name
    logdir.mkdir(parents=True, exist_ok=True); skdir.mkdir(parents=True, exist_ok=True)

    sess = None if a.no_log else (latest_session(project) if a.session == "latest" else Path(a.session))
    if a.no_log:
        print("log: skipped (--no-log)")
    elif sess and sess.exists():
        pairs = turn_pairs(sess)
        out = logdir / f"{datetime.date.today()}-session.md"
        blocks = []
        for u, reply in pairs:
            blocks.append("> " + u.replace("\n", "\n> ") + ("\n\n⏺ " + reply.replace("\n", "\n⏺ ") if reply else ""))
        out.write_text(f"# {name} — session {sess.stem[:8]} in {project.name}: what I typed (>) and Claude's text replies (⏺)\n\n"
                       + "\n\n".join(blocks) + "\n")
        print(f"wrote {out} ({len(pairs)} user turns, with Claude's text replies). Review it before pushing.")
    else:
        print("no Claude Code session found for this project; skipping log")

    for sk in chosen:
        shutil.copy(sk, skdir / f"{sk.parent.name}.SKILL.md")
    print(f"copied {len(chosen)} skill(s) to {skdir}: {', '.join(sk.parent.name for sk in chosen) or '-'}")

    cmp = root / "compare.py" if (root / "compare.py").exists() else Path(__file__).with_name("compare.py")
    subprocess.run([sys.executable, str(cmp), str(root)], check=False)
    if a.push:
        subprocess.run(["git", "add", "-A", str(root)], cwd=exchange, check=True)
        subprocess.run(["git", "commit", "-m", f"exchange: {name} shares session input and skills"], cwd=exchange, check=False)
        subprocess.run(["git", "push"], cwd=exchange, check=False)

if __name__ == "__main__":
    main()
