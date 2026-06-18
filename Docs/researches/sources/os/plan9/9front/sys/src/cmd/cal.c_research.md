# File Research: sources/os/plan9/9front/sys/src/cmd/cal.c

Purpose: Plan 9 `cal` command for printing a month or full year calendar.

Key points:
- Supports `-s 1..7` to choose the starting weekday.
- With no arguments, prints the current month. With one argument, interprets a month name/number as current-year month or otherwise a year. With two arguments, prints month and year.
- Uses `Biobuf` for output.
- `number` maps month names and abbreviations to negative month numbers and parses numeric strings.
- `cal` lays out month text into a fixed buffer, handling leap years and the 1752 calendar change.
- `jan1` computes weekday for January 1 with Julian/Gregorian adjustment.
- `curmo` and `curyr` use Plan 9 `localtime`.

Dependencies and interactions:
- Uses Plan 9 headers `<u.h>`, `<libc.h>`, and `<bio.h>`.
- Standalone command, no repository-local helper files.

Research notes:
- Historical calendar behavior is embedded directly, including September 1752 shortened to 19 days and skipped dates handling.
- Output formatting is fixed-width and buffer-oriented rather than dynamically structured.
