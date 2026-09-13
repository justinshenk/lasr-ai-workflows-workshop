---
name: share
description: Share what I typed in this session and my skills to the cohort exchange, then regenerate the comparison. Use when the user says "share my session", "post my log", or "/share".
disable-model-invocation: true
---
Share $ARGUMENTS's work to the exchange.

1. Run `uv run python exchange/share.py $ARGUMENTS`. It writes only the user turns of the latest
   session for this project to `exchange/logs/$ARGUMENTS/`, copies `.claude/skills/*/SKILL.md` to
   `exchange/skills/$ARGUMENTS/`, and regenerates `exchange/COMPARISON.md` and `.html`.
2. Open the new log file and show the user the first and last three turns. Ask them to confirm
   nothing private is in it (API keys, unpublished results). Do not push until they say yes.
3. On yes: `git add exchange && git commit -m "exchange: $ARGUMENTS shares session input and skills" && git push`.
4. Tell them where to look: `exchange/COMPARISON.html`, one column per person.
