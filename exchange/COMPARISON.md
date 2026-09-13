# Comparison: what each person typed, and what they've made reusable

| Person | Prompts | Median words / prompt | Prompts mentioning a check | Questions asked | Skills shared |
|---|---|---|---|---|---|
| hana | 2 | 48 | 2 | 1 | 0 |
| justin | 7 | 18 | 1 | 3 | 2 |
| priya | 1 | 78 | 1 | 0 | 0 |
| quinn | 1 | 32 | 0 | 0 | 0 |
| sam | 1 | 58 | 1 | 0 | 0 |
| sim-fellow | 1 | 117 | 1 | 0 | 0 |

## hana

**User input, in order** (`2026-09-13-session.md`); Claude's reply indented under each
1. I'll do the modelling myself. Just give me a tiny script dump_acts.py that saves GPT-2 layer-6 mean-pooled activations and labels for data/train.json and data/ood.json to .npy files using extract.py (activations(texts, layer=6), load_split(path)). Run it with HF_HUB_OFFLINE=1 uv run python and confi
   > I'll check the two helper signatures in extract.py, write the script, and run it.  Done. `dump_acts.py` is written and ran offline. It saved four files in the working directory: `train_X.npy`, `train_y.npy`, `ood_X.npy`, `ood_y.npy`.  Shapes:  | split | X | y | |---|---|---| | train | (60, 768) | (6
2. ok thanks. I trained a logistic regression on the train activations myself with a 70/30 split and got 100% held-out. does that seem right to you? anything I should check before I write it up as 'sentiment direction found'? you can run things if you want, the .npy files are here.
   > A 100% on 18 held-out points from templated data is easy to get for the wrong reasons, so let me look at how the data was made and run a few controls.  Your 100% is real for the train distribution, but it is not evidence of a sentiment direction. It fails the out-of-distribution set almost completel


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


## priya

**User input, in order** (`2026-09-13-session.md`); Claude's reply indented under each
1. 10-minute exercise. Goal: a linear probe for sentiment on GPT-2 layer-6 activations, held-out accuracy, plus one sanity check that the direction is about sentiment. Before writing any code, list the three most likely ways a probe like this could give a misleading accuracy on this data (look at data/
   > I'll look at the data and extract.py first, then list the risks before writing the probe.  Done. The probe trains in seconds, and both risk tests ran. Script is `probe_p.py`.  **Held-out accuracy**  | Split | Accuracy | |---|---| | Random stratified 5-fold CV | 1.000 ± 0.000 | | Dedup + leave-adject


## quinn

**User input, in order** (`2026-09-13-session.md`); Claude's reply indented under each
1. train a linear probe on gpt2 layer 6 activations for sentiment using data/train.json and extract.py (activations(texts, layer=6), load_split(path)). report held out accuracy. run with HF_HUB_OFFLINE=1 uv run python. write it as probe_q.py
   > I'll look at extract.py and the data first, then write probe_q.py and run it.  Done. `probe_q.py` is written and runs offline with the requested command.  **Result**  | Split | n | Accuracy | |---|---|---| | Train | 39 | 1.000 | | Held-out (30%, grouped by text) | 21 | 1.000 | | ood.json (bonus) | 1


## sam

**User input, in order** (`2026-09-13-session.md`); Claude's reply indented under each
1. Train a linear probe for sentiment on GPT-2 layer-6 activations (extract.py: activations(texts, layer=6), load_split(path); data/train.json; run with HF_HUB_OFFLINE=1 uv run python; write probe_s.py). Report held-out accuracy. Then try to break your own result: find the simplest, most boring feature
   > I'll look at the extraction helper and the data first, then train the probe and stress-test the score.  The probe gets a perfect held-out score, and that score is mostly a negation detector plus a sentence-length cue. The script is at `probe_s.py` and runs with the offline flag as requested.  **Held


## sim-fellow

**User input, in order** (`2026-09-13-session.md`); Claude's reply indented under each
1. I'm a research fellow doing a 10-minute exercise in this repo. Task: train a linear probe that separates positive from negative sentences using GPT-2 layer-6 activations, and report held-out accuracy. Then do one sanity check that convinces you the direction is about sentiment and not something else
   > I'll look at extract.py and the data files, write fellow_probe.py, run it, and report.  Done. Script is `fellow_probe.py`, run with `HF_HUB_OFFLINE=1 uv run python fellow_probe.py`.  **Held-out accuracy is perfect on the in-distribution data, but the direction is not sentiment.** It is mostly a "con
