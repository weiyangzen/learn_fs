# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/test/getround.c

Shared helper for gdtoa tests to parse and report directed rounding modes.

`getround(int r, char *s)`:
- With no argument, prints current mode.
- Accepts modes `0` toward zero, `1` nearest, `2` toward +Infinity, `3` toward -Infinity.
- If `Honor_FLT_ROUNDS` is defined, maps modes to `<fenv.h>` constants and calls `fesetround`.

Optional `USE_MY_LOCALE` block supplies a custom `localeconv()` with decimal point `"<Pt>"`.

Dependencies: optional `fenv.h`, optional `locale.h`.
