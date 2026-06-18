# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopd.c

Purpose: Parses a string into double storage using current rounding when enabled.

Core behavior:
- Uses IEEE double `FPI {53, ...}`.
- Calls `strtodg`, then packs the result with `ULtod`.
- Returns `STRTOG_NoMemory` without packing on allocation failure.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h`, `strtodg`, and `ULtod`.
