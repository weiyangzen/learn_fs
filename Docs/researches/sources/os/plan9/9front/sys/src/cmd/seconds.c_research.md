# File Research: sources/os/plan9/9front/sys/src/cmd/seconds.c

Purpose: Converts absolute date/time strings to seconds since the epoch.

Behavior:
- Optional `-f fmt` parses using a user-supplied `tmparse` format.
- Without `-f`, tries known asctime/RFC3339 forms, then combinations of date, time, and zone formats.
- Loads local timezone via `tzload("local")`.
- Rejects trailing non-space junk.
- Prints `tmnorm(&tm)` per input argument.

Integration: Uses Plan 9 time parsing formats and `Tm`/`Tzone`.

Risks:
- Inputs are per argv item, so shell quoting is required for dates with spaces.
- On first unparseable input, calls `sysfatal`.
