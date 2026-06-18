# File Research: sources/os/bsd/netbsd-src/sys/sys/debug.h

Declares small kernel debug initialization and free-check instrumentation hooks.

Key content:
- Requires `_KERNEL`; user-level inclusion is rejected with `#error`.
- `debug_init`.
- `freecheck_out` and `freecheck_in`.
- Macros `FREECHECK_OUT` and `FREECHECK_IN`.

Important behavior:
- Free-check macros call real functions only when both `DEBUG` and `_HARDKERNEL` are defined.
- Otherwise they compile away.
