# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/venust.c

Venus perturbation coefficient data.

Key points:
- Defines `venfp[]`, zero-delimited coefficient/phase subseries.
- Defines `vencp[]`, signed argument multiplier bytes.
- Used by `venus.c` with the shared trigonometric series helpers.

Dependencies:
- Data format is coupled to `cosadd.c`.

Notable behavior:
- Contains no executable logic.
