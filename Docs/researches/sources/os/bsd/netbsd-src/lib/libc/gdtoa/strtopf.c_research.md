# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtopf.c

Purpose: Parses a string into IEEE float storage.

Core behavior:
- Uses float `FPI {24, ...}`.
- Calls `strtodg`.
- Packs zero, normal, denormal, infinity, NaN, and NaN payload values into one `ULong`.
- Sets sign bit from `STRTOG_Neg`.

Dependencies:
- Includes `gdtoaimp.h`.
- Uses optional `gdtoa_fltrnds.h`, `strtodg`, and `f_QNAN`.
