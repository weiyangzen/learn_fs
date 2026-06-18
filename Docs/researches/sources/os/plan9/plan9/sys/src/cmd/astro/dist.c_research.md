# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/dist.c

General astronomical utilities for angular distance, event collection, rise/set interpolation, line reading, and token skipping.

Key points:
- `dist` computes angular separation in arcseconds.
- `rise`, `set`, `solstice`, `betcross`, and `melong` find crossings/extrema over sampled object points.
- `event` records filtered events; `evflush` sorts and prints them.
- `rline` reads one line from a file descriptor into global `line`.
- `skip` advances to field `n` in global `line`.

Dependencies:
- Uses global object sample arrays and event flags.

Notable behavior:
- Significant events sort before ordinary events by subtracting a large offset during comparison.
