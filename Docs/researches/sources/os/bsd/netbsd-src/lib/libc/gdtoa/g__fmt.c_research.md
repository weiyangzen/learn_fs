# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/g__fmt.c

Purpose: Shared final formatter for `g_*fmt` decimal output.

Core behavior:
- Converts a raw digit buffer plus decimal point position into printable form.
- Emits fixed notation when the decimal point is in a compact range.
- Emits exponent notation when `decpt <= -4` or the exponent is far beyond the digit count.
- Inserts sign and locale decimal point when `USE_LOCALE` is enabled.
- Checks `bufsize` before writing and returns `NULL` on insufficient space.
- Frees the temporary `gdtoa` digit buffer before returning.

Dependencies:
- Includes `gdtoaimp.h` and optionally `locale.h`.
- Uses `localeconv`, `MALLOC`, `strcpy`, `strlen`, and `freedtoa`.
