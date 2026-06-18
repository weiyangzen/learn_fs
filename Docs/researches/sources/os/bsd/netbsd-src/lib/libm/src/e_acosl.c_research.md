# File Research: sources/os/bsd/netbsd-src/lib/libm/src/e_acosl.c

Implements long-double `acosl`.

Key behavior:
- Active only under `__HAVE_LONG_DOUBLE`.
- Pulls rational approximation coefficients from `../ld80/invtrig.h` or `../ld128/invtrig.h`.
- Handles `|x| >= 1`, tiny inputs, negative and positive large halves.
- Uses `sqrtl` and long-double significand truncation for the correction term.
- Has an i386 workaround for long-double pi constants.
