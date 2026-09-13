# Comparison: what each person typed, and what they've made reusable

| Person | Prompts | Median words / prompt | Prompts mentioning a check | Questions asked | Skills shared |
|---|---|---|---|---|---|
| justin | 7 | 18 | 1 | 3 | 2 |

## justin

**Skills shared**
- `sanity-check.SKILL.md` — Before reporting any accuracy, probe score, or "it works" claim from an ML experiment, run the four checks below and grade the claim. Use whenever a result is a
- `share.SKILL.md` — Share what I typed in this session and my skills to the cohort exchange, then regenerate the comparison. Use when the user says "share my session", "post my log

**User input, in order** (`2026-09-13-session.md`); Claude's reply indented under each
1. This is for a worktest for Lasr labs research coordinator / manager. I'll need to save process logs.
   > I'll take a look at what's in the working directory first, then set up a process log so we capture the work as we go.  The working directory is empty, so I created `PROCESS_LOG.md` in it with a header and a first timestamped entry. Every step from here on gets appended there with a timestamp, what w
2. [LASR work-test brief pasted here. Redacted: the assessment instructions are not public.]
   > Let me log the brief and your draft first, then give you a straight assessment. Time matters here, so I'll be brief.  Logged, and there's a submission skeleton ready. Here's my honest read on your draft before we build anything, because the choice determines the next 90 minutes.  **The peer-sharing 
3. search for best practices first
   > I'll run a quick, time-boxed search on best practices for systematic AI use in research and Claude Code workflows, then log what's worth using.  Search done and logged. It took about 8 minutes. Here's what matters, and it sharpens the choice rather than changing it.  **What the sources converge on**
4. note, i'm watching a video Best Practices in AI-Assisted Research with Richie (Vegan Hacktivists) - 2026/09/09 17:27 UTC - Recording
   > Environment is installing in the background, and the video is logged. Two things I need from you when the recording finishes:  1. **The direction call:** verification-first loop, or your peer-sharing design. 2. **Anything from Richie's talk worth folding in.** A few bullets is enough. Practices that
5. I still think peer-sharing is valuable, particularly for researchers who may tend to work independently. i'd consider including those resources as high level advice, and ask people what has worked for them, along with a worked example.
   > Understood, peer-sharing stays as the core and the research is folded in as high-level advice. That's your call and it's a defensible one: fellows in small teams who work independently benefit from seeing each other's habits. I'll now build it as strongly as the brief allows. Logging the decision an
6. is there not a simple way to allow uploading process logs and skills?
   > Yes. I over-built it. A shared page with a custom uploader is not the simplest thing, and it isn't the most natural one for this cohort either. Let me check what's available for the simplest options before recommending.  There are two genuinely simple ways, and both beat the custom page.  **Option 1
7. then to compare the process logs and skills in one view? particularly user input
   > That's the real need: put everyone's prompts side by side. The most revealing comparison is what each person typed, not what the model produced. A small script in the repo can do that: read every log in `exchange/logs/`, pull out the user turns, list each person's skills, and render one comparison p

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
