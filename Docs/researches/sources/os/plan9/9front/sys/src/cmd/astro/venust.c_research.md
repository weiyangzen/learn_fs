# File Research: sources/os/plan9/9front/sys/src/cmd/astro/venust.c

Venus perturbation data tables.

Important contents:
- `venfp` stores coefficient/phase pairs separated into groups by zero sentinels.
- `vencp` stores signed multipliers for Venus/Earth/Mars/Jupiter arguments.
- Used by `venus.c` to compute perturbations.

This is data-only support for Venus ephemeris calculations.
