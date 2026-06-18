# File Research: sources/os/plan9/9front/sys/src/cmd/sleep.c

Purpose: Sleeps for a requested number of seconds, with optional millisecond fraction.

Behavior:
- Avoids floating point for bootstrap usefulness.
- Sleeps in chunks no larger than `MAXSEC` to avoid millisecond overflow.
- Parses fractional part to three decimal digits and sleeps remaining milliseconds.
- No argument exits immediately.

Risks:
- Fraction parsing truncates beyond three digits by mutating `p[3]`.
- Negative or malformed inputs mostly result in no sleep or integer parser behavior.
