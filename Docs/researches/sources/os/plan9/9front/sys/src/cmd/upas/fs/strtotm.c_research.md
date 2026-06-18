# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/strtotm.c

This file parses many mail date string formats into `Tm`.

Key behavior:
- Tries a list of `tmparse` patterns covering ctime-like dates, RFC-ish dates, dash-separated dates, and slash dates with optional weekdays/timezones.
- Returns `0` on first successful parse, `-1` if no format matches.

Integration and risks:
- Used by Plan 9 mbox parsing, MIME/header date logic, and the test helper.
