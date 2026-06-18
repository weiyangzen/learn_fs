# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vfwscanf.c

Implements the wide scanf engine: `vfwscanf()`, `vfwscanf_l()`, and `__vfwscanf_unlocked_l()`. It reads with `__fgetwc_unlock()`, pushes back with `ungetwc()`, supports size modifiers, assignment suppression, width, `%n`, integer/pointer scanning, floating-point scanning, wide scansets, and both wide and multibyte output destinations for `%c`, `%s`, and `%[`.

Its `parsefloat()` mirrors the narrow scanner with wide characters, recognizing signs, decimal/hex mantissas, exponents, `inf`, `infinity`, and `nan(...)`, then rewinding to the last valid commit. Non-long string/char conversions convert wide input back to multibyte with `wcrtomb_l()`.
