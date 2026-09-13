"""End-to-end checks for share.py and compare.py on synthetic data. Run from probe-demo."""
import json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

REPO = Path("/Users/justinshenk/projects/lasr-worktest/probe-demo").resolve()
SHARE = REPO / "plugins/lasr-exchange/scripts/share.py"
COMPARE = REPO / "exchange/compare.py"
fails = []
def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg); fails.append(msg) if not cond else None

tmp = Path(tempfile.mkdtemp())
ex = tmp / "exchange"; (ex / "logs").mkdir(parents=True); (ex / "skills").mkdir()

# --- person A: synthetic Claude Code jsonl with user text, tool_result-only user entries, assistant text + tool_use, meta ---
def j(**k): return json.dumps(k)
a = ex / "logs/alice"; a.mkdir()
(a / "s.jsonl").write_text("\n".join([
    j(type="user", message={"content": "train a probe on layer 6"}),
    j(type="assistant", message={"content": [{"type":"text","text":"Sure, writing probe.py"}, {"type":"tool_use","name":"Bash","input":{"command":"rm -rf /"}}]}),
    j(type="user", message={"content": [{"type":"tool_result","content":"SECRET_TOOL_OUTPUT"}]}),
    j(type="assistant", message={"content": [{"type":"text","text":"Held-out accuracy 1.00"}]}),
    j(type="user", isMeta=True, message={"content": "meta line should be skipped"}),
    j(type="user", message={"content": "<system-reminder>skip me</system-reminder>"}),
    j(type="user", message={"content": "now add a shuffled-label control & check OOD <b>x</b>"}),
    j(type="assistant", message={"content": [{"type":"text","text":"<script>alert(1)</script> Shuffled: 0.49"}]}),
    "not json at all",
]))
sk = ex / "skills/alice"; sk.mkdir()
(sk / "sanity.SKILL.md").write_text("---\nname: sanity\ndescription: Four checks before claiming.\n---\nbody")

# --- person B: share.py-style text with > and ⏺ ---
b = ex / "logs/bob"; b.mkdir()
(b / "t.md").write_text("# bob\n\n> first prompt\n> second line of first prompt\n\n⏺ reply one\n⏺ reply line two\n\n> verify the result\n\n> third prompt with no reply\n")

# --- person C: User:/Assistant: transcript + a notes file + a skill with no frontmatter ---
c = ex / "logs/carol"; c.mkdir()
(c / "chat.txt").write_text("User: hello there\nAssistant: hi\nUser: test it please\nAssistant: ok\nUser: bye\n")
(c / "notes.md").write_text("should be ignored by parser (notes prefix)")
(c / "plain.txt").write_text("free-form notes with no markers")
skc = ex / "skills/carol"; skc.mkdir(); (skc / "prompt.md").write_text("Always print failures first.\nmore")

# --- run compare ---
r = subprocess.run([sys.executable, str(COMPARE), str(ex)], capture_output=True, text=True)
check(r.returncode == 0, f"compare.py exit 0 ({r.stderr.strip()[-200:]})")
md = (ex / "COMPARISON.md").read_text(); html = (ex / "COMPARISON.html").read_text()
check("| alice | 2 |" in md, "alice: 2 user turns (tool_result, meta, <system> skipped)")
check("| bob | 3 |" in md, "bob: 3 user turns from > format")
check("| carol | 3 |" in md, "carol: 3 user turns from User: format")
check("SECRET_TOOL_OUTPUT" not in md and "SECRET_TOOL_OUTPUT" not in html, "tool_result content never reaches output")
check("rm -rf" not in html, "tool_use input never reaches output")
check("<script>alert(1)</script>" not in html and "&lt;script&gt;" in html, "assistant text is HTML-escaped")
check("&lt;b&gt;x&lt;/b&gt;" in html, "user text is HTML-escaped")
check(html.count("<section>") == 3, "one column per person")
check(html.count("<details>") == 2 + 1 + 2, f"reply dropdowns: alice 2, bob 1, carol 2 (bye has no reply) (got {html.count('<details>')})")
check("reply line two" in html and "second line of first prompt" in html, "multi-line > and ⏺ blocks preserved")
check("no text reply captured" in html, "prompt with no reply is labelled")
check("Four checks before claiming." in md and "Always print failures first." in md, "skill descriptions: frontmatter and first-line fallback")
check("free-form notes" in md and "should be ignored" not in md, "plain file → notes; notes*.md skipped")
m = re.search(r"\| alice \| 2 \| \d+ \| (\d+) \|", md); check(m and m.group(1) == "1", "check-word highlighting counts alice's 'control & check' prompt once")

# --- share.py: synthetic project + session, no push ---
proj = tmp / "proj"; (proj / ".claude/skills/myskill").mkdir(parents=True)
(proj / ".claude/skills/myskill/SKILL.md").write_text("---\nname: myskill\ndescription: d\n---\n")
sess = tmp / "sess.jsonl"; sess.write_text((a / "s.jsonl").read_text())
r = subprocess.run([sys.executable, str(SHARE), "Dave Smith", "--project", str(proj), "--exchange", str(tmp), "--session", str(sess)],
                   capture_output=True, text=True)
check(r.returncode == 0, f"share.py exit 0 ({r.stderr.strip()[-300:]})")
dl = list((ex / "logs/dave-smith").glob("*-session.md"))
check(len(dl) == 1, "share.py wrote one log under a sanitised name (dave-smith)")
log = dl[0].read_text() if dl else ""
check(log.count("\n> ") + log.count("> ", 0, 2) >= 2 and "⏺ " in log, "log has > user lines and ⏺ reply lines")
check("SECRET_TOOL_OUTPUT" not in log and "rm -rf" not in log and "meta line" not in log, "share.py log excludes tool output, tool_use, meta")
check((ex / "skills/dave-smith/myskill.SKILL.md").exists(), "share.py copied project skill")
check("| dave-smith | 2 |" in (ex / "COMPARISON.md").read_text(), "share.py regenerated comparison including dave-smith")
# round-trip: compare.py must parse share.py's own output identically to the jsonl
md2 = (ex / "COMPARISON.md").read_text()
check(md2.count("now add a shuffled-label control") == 2, "round-trip: share.py text log parses to the same prompts as the jsonl")

# --- share.py: missing exchange, no repo → clean error, not a traceback ---
r = subprocess.run([sys.executable, str(SHARE), "x", "--project", str(proj), "--exchange", str(tmp / "nope"), "--session", str(sess)], capture_output=True, text=True)
check(r.returncode != 0 and "Traceback" not in r.stderr and "not found" in (r.stderr + r.stdout), "missing exchange dir → clean error message")

# --- share.py: no session found ---
r = subprocess.run([sys.executable, str(SHARE), "x", "--project", str(tmp / "proj"), "--exchange", str(tmp), "--session", str(tmp / "missing.jsonl")], capture_output=True, text=True)
check(r.returncode == 0 and "no Claude Code session found" in r.stdout, "missing session → skips log, still runs")

# --- selection flags ---
r = subprocess.run([sys.executable, str(SHARE), "eve", "--project", str(proj), "--exchange", str(tmp), "--session", str(sess), "--list"], capture_output=True, text=True)
check(r.returncode == 0 and "SKILLS found" in r.stdout and "myskill" in r.stdout and not (ex / "logs/eve").exists(), "--list previews and writes nothing")
r = subprocess.run([sys.executable, str(SHARE), "eve", "--project", str(proj), "--exchange", str(tmp), "--session", str(sess), "--skills", "none"], capture_output=True, text=True)
check(r.returncode == 0 and not list((ex / "skills/eve").glob("*")) and list((ex / "logs/eve").glob("*")), "--skills none shares log only")
r = subprocess.run([sys.executable, str(SHARE), "fay", "--project", str(proj), "--exchange", str(tmp), "--session", str(sess), "--no-log", "--skills", "myskill"], capture_output=True, text=True)
check(r.returncode == 0 and (ex / "skills/fay/myskill.SKILL.md").exists() and not (ex / "logs/fay").glob("*-session.md").__next__ if False else r.returncode == 0 and (ex / "skills/fay/myskill.SKILL.md").exists() and not list((ex / "logs/fay").glob("*-session.md")), "--no-log --skills myskill shares the named skill only")
r = subprocess.run([sys.executable, str(SHARE), "gus", "--project", str(proj), "--exchange", str(tmp), "--session", str(sess), "--skills", "nope"], capture_output=True, text=True)
check(r.returncode != 0 and "not found" in (r.stderr + r.stdout) and not (ex / "logs/gus").exists(), "unknown skill name → error before writing anything")

shutil.rmtree(tmp)
print(f"\n{len(fails)} failure(s)")
sys.exit(1 if fails else 0)
