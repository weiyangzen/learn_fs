# File Research: sources/os/plan9/9front/sys/src/cmd/astro/dist.c

General helpers for angular distances, rise/set interpolation, event queueing, and small parsing/math utilities.

Important behavior:
- `dist` computes angular separation in arcseconds.
- `rise`, `set`, `solstice`, `betcross`, and `melong` locate events from sampled object points.
- `event` filters by darkness/light constraints and queues event messages.
- `evflush` sorts events, prints them, and supports significant-event wording.
- `rline`, `pyth`, and `skip` provide input and numerical helpers.

This file is central to turning sampled ephemeris data into human-readable event output.
