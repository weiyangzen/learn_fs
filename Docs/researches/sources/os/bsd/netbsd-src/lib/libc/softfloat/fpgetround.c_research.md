# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetround.c

Read completely: 55 lines.

Implements `fpgetround()` for the software FP environment. It returns the current `float_rounding_mode` and provides weak alias `_fpgetround`.

Risk: no validation or conversion here; callers receive the raw softfloat rounding-mode value.
