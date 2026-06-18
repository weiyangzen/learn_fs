# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtof.c

Purpose: Implements locale-aware `strtof`/`strtof_l` for IEEE float.

Core behavior:
- `_int_strtof_l()` parses with `strtodg` and `FPI {24, ...}`.
- Packs normal, denormal, infinity, NaN, and NaN payload results into one float word.
- Applies the sign bit from `STRTOG_Neg`.
- Returns `HUGE_VALF` and sets `errno` on no-memory.
- Public wrappers use `_current_locale()` or an explicit locale.

Dependencies:
- Includes NetBSD namespace headers, `gdtoaimp.h`, `<locale.h>`, and `setlocale_local.h`.
- Uses optional `gdtoa_fltrnds.h` for current rounding mode.
