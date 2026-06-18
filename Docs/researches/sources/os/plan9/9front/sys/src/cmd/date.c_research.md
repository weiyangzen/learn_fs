# File Research: sources/os/plan9/9front/sys/src/cmd/date.c

Purpose: Plan 9 `date` command.

Key behavior:
- Supports `-n` normalized seconds output, `-u` UTC/no local timezone, `-t` ISO-like timestamp, `-i` date-only, and `-f fmt`.
- With no argument, uses `nsec()` for current seconds and nanoseconds.
- With one argument, treats it as epoch seconds.
- Loads local timezone with `tzload("local")` unless `-u`.
- Converts with `tmtimens()` and formats via `tmfmt()`.

Notable details:
- Default format is `WW MMM _D hh:mm:ss ZZZ YYYY`.
- `-n` prints `tmnorm(&tm)` rather than formatted calendar text.
