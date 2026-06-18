# File Research: sources/os/plan9/9front/sys/src/cmd/dict/comfix.awk

Purpose: Expands comma-abbreviated dictionary raw index entries into fuller word forms.

Key behavior:
- For two-field rows with commas in field 2, splits the term list on comma+spaces.
- Prints the base word unchanged.
- For each suffix:
  - if it is one letter, replaces the last letter of the base word,
  - otherwise searches backward in the base word for the suffix’s first letter and accepts the replacement if the matched old suffix length is within three characters of the new suffix length.
- If suffix matching fails, preserves the unresolved `base, suffix` form for manual cleanup.
- Non-two-field rows pass through unchanged.

Notable details:
- Intended for raw index patterns such as `problematico, a, ci, che`.
