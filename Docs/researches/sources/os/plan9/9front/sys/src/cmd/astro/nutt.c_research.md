# File Research: sources/os/plan9/9front/sys/src/cmd/astro/nutt.c

Nutation coefficient tables.

Important contents:
- `nutfp` contains coefficient/phase pairs grouped by zero sentinels.
- `nutcp` contains integer multipliers for nutation arguments.
- Used by `nutate.c` to compute long and short period terms.

This is data-only support for Earth nutation calculations.
