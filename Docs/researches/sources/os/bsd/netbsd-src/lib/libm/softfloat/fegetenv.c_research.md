# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/fegetenv.c

Implements `fegetenv`.

Key behavior:
- Stores sticky exception flags, exception mask, and rounding mode into `fenv_t`.
- Uses `__FENV_SET_FLAGS`, `__FENV_SET_MASK`, and `__FENV_SET_ROUND`.
- Always returns 0.
