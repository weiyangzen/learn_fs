# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtold_subr.c

Purpose: Shared include file for format-specific `strtold` implementations.

Core behavior:
- Requires the including file to define `GDTOA_LD_FMT`.
- Builds `STRTOP(GDTOA_LD_FMT)` into a call to `strtopQ`, `strtopx`, or `strtopxL`.
- Implements `_int_strtold_l()`, `strtold()`, and `strtold_l()`.
- Uses `_current_locale()` for the non-locale API.
- Requires `__HAVE_LONG_DOUBLE`.

Dependencies:
- Includes NetBSD namespace headers, `<math.h>`, `<stdlib.h>`, `gdtoa.h`, `<locale.h>`, and `setlocale_local.h`.
