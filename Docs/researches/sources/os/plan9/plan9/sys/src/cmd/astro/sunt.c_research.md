# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/sunt.c

Solar perturbation coefficient data.

Key points:
- Defines `sunfp[]`, zero-delimited coefficient/phase subseries.
- Defines `suncp[]`, compact multiplier bytes for the trigonometric series.
- Used by `sun.c` through `icosadd`, `cosadd`, and `sinadd`.

Dependencies:
- Data format is tied to `cosadd.c`.

Notable behavior:
- Contains no functions.
