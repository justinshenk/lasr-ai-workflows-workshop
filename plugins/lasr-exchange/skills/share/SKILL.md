---
name: share
description: Post what I typed in this session and my project's skills to the LASR cohort exchange, then regenerate the one-view comparison. Use for "/share <name>", "share my session", "post my log".
disable-model-invocation: true
---
Share $ARGUMENTS's session input and skills to the cohort exchange.

1. Run:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/share.py" $ARGUMENTS --project "$PWD"`
   It clones the exchange repo to `~/lasr-exchange` on first use (from `$LASR_EXCHANGE_REPO`), writes
   ONLY the user turns of this project's latest session to `exchange/logs/$ARGUMENTS/`, copies
   `.claude/skills/*/SKILL.md` to `exchange/skills/$ARGUMENTS/`, and regenerates `COMPARISON.md`/`.html`.
   If it exits saying no repo is configured, ask the user for the exchange repo URL and re-run with `--repo <url>`.
2. Show the user the first three and last three lines of the new log file. Ask them to confirm nothing
   private is in it (API keys, unpublished results). Do not push until they say yes.
3. On yes, re-run the same command with `--push`.
4. Tell them: open `~/lasr-exchange/exchange/COMPARISON.html` for one column per person.
