# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/pdate.c

Date/time conversion and printing utilities for `astro`.

Key points:
- Converts between internal day counts and calendar fields with `convdate`, `dtsetup`, and `dsrc`.
- Prints numeric or speech-like dates/times depending on `flags['s']`.
- `pstime` prints sidereal/location-related position context.
- `tzone` adjusts for local timezone using Plan 9 `localtime`/`gmtime`.
- Handles Gregorian calendar correction and BC year adjustment.

Dependencies:
- Uses global flags, observer location, and `helio`/`geo` for `pstime`.

Notable behavior:
- Internal epoch is relative to 1900-style astronomical day counts.
