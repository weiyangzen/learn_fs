# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/main.c

Main driver and argument parser for `astro`.

Key points:
- Initializes constants, formatters, object table, arguments, and observer location.
- For each requested period, samples every object at `NPTS+2` times unless point/distance mode is requested.
- Supports direct position printing, object distance mode, event search mode, date input, local timezone correction, comet-only display, and custom periods.
- Reads default location from `/lib/sky/here`, with fallback coordinates.

Dependencies:
- Coordinates all `astro` modules.

Notable behavior:
- `deltat` is heuristically derived from date unless explicitly read with `-t`.
