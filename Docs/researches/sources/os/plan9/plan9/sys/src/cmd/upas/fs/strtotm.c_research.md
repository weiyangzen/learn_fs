# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/strtotm.c

## Purpose
Heuristic RFC822-ish date string parser used by mailfs to convert mail dates into Plan 9 `Tm`.

## Main Interfaces
- `strtotm(char *p, Tm *tmp)`: scans free-form date text for month, day, year, time, zone, and numeric offset.

## Behavior
The parser tokenizes by whitespace, recognizes `hh:mm[:ss]`, three-letter month names case-insensitively, three-letter all-caps zones ending in `T`, numeric `+/-HHMM` offsets, day numbers, and years. It converts with `tm2sec` minus the offset and returns localtime of the resulting epoch.

## Dependencies
Plan 9 `Tm`, `localtime`, `tm2sec`; C `ctype`.

## Risks / Notes
- Time zone abbreviations are copied but only numeric offsets affect conversion.
- Two-digit years are not accepted as years.
- Parsing is permissive and order-insensitive, intended as a fallback heuristic.
