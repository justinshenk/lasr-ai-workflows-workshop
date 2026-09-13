"""Post what you typed in your latest Claude Code session, plus your project's skills, to the cohort exchange.

    python share.py <your-name> [--project DIR] [--exchange DIR] [--repo URL] [--session latest|PATH] [--push]

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
    a = ap.parse_args()

    project, exchange = Path(a.project).resolve(), Path(a.exchange).expanduser().resolve()
    if not exchange.exists():
        if not a.repo: sys.exit(f"{exchange} not found and no --repo / $LASR_EXCHANGE_REPO to clone from.")
        subprocess.run(["git", "clone", a.repo, str(exchange)], check=True)
    root = exchange / "exchange" if (exchange / "exchange").exists() else exchange
    name = re.sub(r"[^a-z0-9-]", "-", a.name.lower())
    logdir, skdir = root / "logs" / name, root / "skills" / name
    logdir.mkdir(parents=True, exist_ok=True); skdir.mkdir(parents=True, exist_ok=True)

    sess = latest_session(project) if a.session == "latest" else Path(a.session)
    if sess and sess.exists():
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

    n = 0
    for sk in (project / ".claude" / "skills").glob("*/SKILL.md"):
        shutil.copy(sk, skdir / f"{sk.parent.name}.SKILL.md"); n += 1
    print(f"copied {n} skill(s) to {skdir}")

    cmp = root / "compare.py" if (root / "compare.py").exists() else Path(__file__).with_name("compare.py")
    subprocess.run([sys.executable, str(cmp), str(root)], check=False)
    if a.push:
        subprocess.run(["git", "add", "-A", str(root)], cwd=exchange, check=True)
        subprocess.run(["git", "commit", "-m", f"exchange: {name} shares session input and skills"], cwd=exchange, check=False)
        subprocess.run(["git", "push"], cwd=exchange, check=False)

if __name__ == "__main__":
    main()
