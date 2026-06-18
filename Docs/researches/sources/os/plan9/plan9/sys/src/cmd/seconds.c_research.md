# File Research: sources/os/plan9/plan9/sys/src/cmd/seconds.c

Date parser that converts absolute date strings to seconds since epoch.

Key behavior:
- Accepts one or more date/time strings and prints unsigned seconds for each.
- Parses month names, day/month/year fields, time fields, AM/PM, named time zones, numeric time zones, and ignored weekday/filler words.
- Supports alternate delimiter handling for DEC-style dates.
- Converts parsed `Tm` through `tm2sec()` after validation.

Important details:
- Years must be representable in an unsigned 32-bit epoch range, effectively 1970 through 2106.
- Time zone token values are compressed in the token table by dividing minutes by 10.
- Numeric tokens are classified by position: first short number is day, later short number is year.
- Missing year/month/day invalidates the date.

Filesystem relevance:
- None directly; small time/date command.
