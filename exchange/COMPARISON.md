# Comparison: what each person typed, and what they've made reusable

| Person | Prompts | Median words / prompt | Prompts mentioning a check | Questions asked | Skills shared |
|---|---|---|---|---|---|
| justin | 7 | 18 | 1 | 3 | 2 |

## justin

**Skills shared**
- `sanity-check.SKILL.md` — Before reporting any accuracy, probe score, or "it works" claim from an ML experiment, run the four checks below and grade the claim. Use whenever a result is a
- `share.SKILL.md` — Share what I typed in this session and my skills to the cohort exchange, then regenerate the comparison. Use when the user says "share my session", "post my log

**User input, in order** (`2026-09-13-session.md`)
1. This is for a worktest for Lasr labs research coordinator / manager. I'll need to save process logs.
2. [LASR work-test brief pasted here. Redacted: the assessment instructions are not public.]
3. search for best practices first
4. note, i'm watching a video Best Practices in AI-Assisted Research with Richie (Vegan Hacktivists) - 2026/09/09 17:27 UTC - Recording
5. I still think peer-sharing is valuable, particularly for researchers who may tend to work independently. i'd consider including those resources as high level advice, and ask people what has worked for them, along with a worked example.
6. is there not a simple way to allow uploading process logs and skills?
7. then to compare the process logs and skills in one view? particularly user input

**Notes** (`probe-run-output.txt`)

```
[1] held-out acc (random split of train.json): 1.00
[2] OOD acc (data/ood.json):                    0.56
[3] on OOD, P(pred=negative | negation present)  = 1.00  (n=3)
    on OOD, P(pred=negative | no negation)       = 0.92  (n=13)
    in train.json, fraction of NEGATIVE examples containing 'not': 0.63; of POSITIVE: 0.00
[4] shuffled-label held-out acc: mean 0.49, max 0.72
[5] which OOD sentences does the naive probe get wrong?
      true=pos pred=neg  I can't recommend this place enough.
      true=pos pred=neg  Not a single dull moment in the whole show.
      true=pos pred=neg  There was nothing I didn't love about it.
      true=pos pred=neg  Never have I had a better night out.
      true=pos pred=neg  The staff couldn't have been kinder.
      true=pos pred=neg  Honestly, it exceeded
```
