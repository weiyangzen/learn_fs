# File Research: sources/os/plan9/9front/sys/src/cmd/astro/merct.c

Mercury perturbation data tables.

Important contents:
- `mercfp` stores coefficient/phase pairs separated by zero sentinels.
- `merccp` stores signed multipliers for the active base arguments.
- The tables feed `cosadd` calls in `merc.c` for longitude and radius corrections.

This is data-only support for Mercury ephemeris calculations.
