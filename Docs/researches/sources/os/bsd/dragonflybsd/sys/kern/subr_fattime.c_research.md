# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_fattime.c

## Summary
Converts between POSIX `timespec` values and MS-DOS FAT date/time fields, including the FAT hundredths/odd-second byte.

## Main Responsibilities
- `timespec2fattime()` encodes date, time, and optional hundredths byte from a `timespec`.
- `fattime2timespec()` decodes FAT date/time/hundredths fields back to a `timespec`.
- Uses lookup tables for month/day placement within four-year leap cycles.
- Handles FAT’s 1980 epoch and the non-leap-year 2100 correction.

## Important Behavior
FAT stores timestamps as local calendar time unless the `utc` argument requests UTC-style conversion. In this DragonFly version, the local-time offset hooks are placeholders using `0`, so UTC and local paths currently do not differ. Dates before 1980 are clamped to 1980-01-01 on encode.

## Risks
Invalid FAT fields are not deeply validated; decode trusts the packed date/time values and table indexing. The optional `TEST_DRIVER` block appears stale relative to exported function names and is not normal kernel build code.
