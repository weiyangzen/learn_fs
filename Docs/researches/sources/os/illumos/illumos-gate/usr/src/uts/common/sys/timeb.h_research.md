# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timeb.h

## Purpose
Legacy System V/BSD `ftime(3C)` interface header.

## Main Interfaces
- Defines `struct timeb` with seconds, milliseconds, timezone offset, and DST flag.
- Declares `ftime(struct timeb *)`.

## Dependencies And Relationships
Includes `sys/types.h` for `time_t`. This is a compatibility header for old applications rather than a preferred time API.

## Research Notes
The interface is obsolete relative to `gettimeofday`, `clock_gettime`, and related APIs, but remains ABI-relevant for legacy source compatibility.
