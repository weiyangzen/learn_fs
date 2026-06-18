# File Research: sources/os/bsd/netbsd-src/lib/libm/src/b_tgammal.c

Implements or dispatches `tgammal`.

Key behavior:
- If `__HAVE_LONG_DOUBLE` is defined, includes the long-double implementation matching `LDBL_MANT_DIG == 64` or `113`.
- Rejects unsupported long-double formats at compile time.
- If long double support is unavailable, implements `tgammal` by delegating to double `tgamma`.
- Exports weak alias `tgammal` to `_tgammal`.
