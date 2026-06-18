# File Research: sources/os/plan9/9front/sys/src/cmd/astro/pdate.c

Calendar conversion and date/time formatting for `astro`.

Important behavior:
- Converts between internal day count and year/month/day/hour/minute fields.
- Handles Julian/Gregorian transition logic and BCE year adjustment.
- Supports local “kitchen clock” correction via Plan 9 `localtime`/`gmtime`.
- Formats plain and speech-like date/time output.
- `pstime` prints apparent sky/time/location context.
- Contains month and number-word tables.

This file isolates user-facing temporal formatting and calendar arithmetic.
