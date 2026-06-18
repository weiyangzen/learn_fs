# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/nutate.c

Computes nutation, obliquity, and Greenwich sidereal time.

Key points:
- Computes lunar/solar arguments and ascending node.
- Uses `nutfp`/`nutcp` coefficient tables through `sinadd`/`cosadd`.
- Sets long-period and short-period nutation terms: `phi`, `eps`, `dphi`, and `deps`.
- Computes mean obliquity, true obliquity, and sidereal time corrected by nutation.

Dependencies:
- Uses coefficient data from `nutt.c`.

Notable behavior:
- Comments describe coefficients as from the Explanatory Supplement.
