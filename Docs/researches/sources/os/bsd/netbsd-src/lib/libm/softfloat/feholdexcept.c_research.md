# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/feholdexcept.c

Implements `feholdexcept`.

Key behavior:
- Saves sticky flags, exception mask, and rounding mode to `fenv_t`.
- Clears sticky flags.
- Disables all exception traps by setting mask to zero.
- Always returns 0.
