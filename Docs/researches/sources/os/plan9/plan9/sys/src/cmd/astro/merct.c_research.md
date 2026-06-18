# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/merct.c

Mercury perturbation coefficient data.

Key points:
- Defines `mercfp[]`, a sequence of coefficient/phase pairs split into zero-terminated subseries.
- Defines `merccp[]`, signed argument multiplier bytes consumed by `cosadd`/`sinadd`.
- Used by `merc.c` to compute longitude and log-radius perturbations.

Dependencies:
- Data format is tightly coupled to `cosadd.c`.

Notable behavior:
- Contains no executable logic beyond static data definitions.
