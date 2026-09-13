---
name: sanity-check
description: Before reporting any accuracy, probe score, or "it works" claim from an ML experiment, run the four checks below and grade the claim. Use whenever a result is about to be written down or shared.
---
# Sanity check before claiming a result

The number I'm about to report: $ARGUMENTS

Do all four. Report each with the actual command run and the actual output, not a summary.

1. **Different generating process.** Evaluate on data that was NOT produced the same way as the
   training data (hand-written, a different template, a different source). If no such set exists,
   write 8–16 examples now and evaluate on them. Report the number next to the original.
2. **Shuffled-label control.** Refit with permuted labels (≥10 times). Report mean and max. If the
   original score is inside that range, the result is noise.
3. **Look at the failures.** Print every misclassified item on the held-out and OOD sets. Say in one
   sentence what they have in common.
4. **Name the simplest non-target explanation.** State the most boring feature that could produce this
   score (length, a token, a template, label leakage, duplicate rows). Test it directly if it takes
   under 2 minutes.

Then grade the original claim: **verified / partially verified / unverified**, with one line of
justification. Do not soften the grade to be encouraging.
