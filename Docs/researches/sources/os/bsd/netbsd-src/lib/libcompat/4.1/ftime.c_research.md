# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.1/ftime.c

## Purpose
Implements historical `ftime()` compatibility API.

## Behavior
Calls `gettimeofday()` with a `struct timezone`, fills `struct timeb` seconds, milliseconds, minutes west of UTC, and DST flag, and returns `0` or `-1`.

## Dependencies
Depends on `sys/time.h`, `sys/timeb.h`, and `_DIAGASSERT`.

## Risks And Notes
This preserves obsolete timezone fields from `gettimeofday()`. The caller must pass a valid `struct timeb *`.
