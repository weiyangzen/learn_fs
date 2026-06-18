# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/nutt.c

Nutation coefficient data.

Key points:
- Defines `nutfp[]`, coefficient/phase-pair series for nutation longitude and obliquity terms.
- Defines `nutcp[]`, compact signed multiplier data used by `cosadd`/`sinadd`.

Dependencies:
- Consumed only by `nutate.c` through `icosadd`.

Notable behavior:
- Contains no executable functions.
