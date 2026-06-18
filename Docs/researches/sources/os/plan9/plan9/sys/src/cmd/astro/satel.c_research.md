# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/satel.c

Artificial satellite pass prediction support.

Key points:
- `satels` reads satellite element files from `satlst`, currently an empty list.
- Parses epoch/orbital parameters, precomputes trig constants, and scans the day in five-minute steps.
- `satel` propagates satellite position, solves eccentric anomaly, checks visibility, and sets elevation.
- `vis` checks sunlight/geometry constraints for satellite and observer.

Dependencies:
- Uses global observer location, date utilities, `sunel`, and event queue.

Notable behavior:
- Because `satlst` contains only `0`, no satellite files are processed unless the table is changed.
