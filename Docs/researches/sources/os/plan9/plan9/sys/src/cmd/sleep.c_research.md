# File Research: sources/os/plan9/plan9/sys/src/cmd/sleep.c

Small sleep command.

Key behavior:
- Sleeps for integer seconds from `argv[1]`.
- Supports a fractional part up to milliseconds without using floating point.
- Exits successfully even with no argument.

Important details:
- Fraction parsing scales one, two, or at least three digits to milliseconds.
- Comment explains avoiding floating point so the command remains useful during machine bootstrap.

Filesystem relevance:
- None.
