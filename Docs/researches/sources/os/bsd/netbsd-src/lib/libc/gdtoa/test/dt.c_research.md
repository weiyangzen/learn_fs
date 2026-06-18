# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/dt.c

Legacy gdtoa/dtoa test harness for double conversion.

It accepts decimal strings or raw `#hex0 hex1[: mode ndigits]` inputs, converts with `strtod`, compares with `atof`, formats with a local `g_fmt` wrapper around `dtoa`, and probes adjacent representable values by incrementing/decrementing the low word.

Important behavior:
- Global `STRTOD_DIGLIM` defaults to `24`.
- `check()` round-trips a `dtoa` result back through `strtod` and reports bit mismatches.
- Handles VAX word adjustments conditionally.
- Prints `dtoa` sign, decimal point, digit count, and digit string for requested mode/precision.

Dependencies: `gdtoa.h`, `dtoa`, `strtod`, platform word-order macros.
