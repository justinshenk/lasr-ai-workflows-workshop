---
name: share
description: Post what I typed in this session and selected skills to the LASR cohort exchange, then rebuild the live comparison page. Use for "/share <name>", "share my session", "post my log".
disable-model-invocation: true
---
Share $ARGUMENTS's session input and skills to the cohort exchange. Nothing is written or pushed
without the user choosing what goes.

1. Preview. Run:
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/share.py" $ARGUMENTS --project "$PWD" --list`
   It prints the user turns it found (first line of each) and the skills in this project's
   `.claude/skills/`. It writes nothing. If it says no session was found, tell the user and continue
   with skills only.
2. Ask, with AskUserQuestion, two things:
   - "Share the session log?" (yes / no). Remind them it contains only what they typed plus Claude's
     text replies, no tool output or file contents, and ask if anything in the preview looks private.
   - "Which skills?" as a multi-select over the skill names found, plus "none".
   Do not assume; wait for the answers.
3. Write. Re-run without `--list`, adding `--skills <comma-separated names or none>` and `--no-log` if they
   declined the log. This clones the exchange repo to `~/lasr-exchange` on first use (from
   `$LASR_EXCHANGE_REPO`; if unset, ask for the URL and pass `--repo`). It writes to
   `exchange/logs/$ARGUMENTS/` and `exchange/skills/$ARGUMENTS/` and regenerates the comparison.
4. Confirm. Show the paths written. Ask "Push to the exchange now?" Only on yes, re-run the same
   command with `--push`.
5. Tell them the push redeploys https://lasr-exchange.vercel.app within about a minute.
