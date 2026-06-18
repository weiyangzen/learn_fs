# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetmask.c

Read completely: 61 lines.

Implements `fpgetmask()` for the software floating-point environment. It returns `float_exception_mask` and exposes a weak alias to `_fpgetmask`.

For `SOFTFLOATM68K_FOR_GCC`, this file also defines the softfloat global state variables for exception flags, exception mask, and rounding mode.

Risk: direct global-state accessor; behavior depends on whether architecture-specific softfloat macros remap the globals.
