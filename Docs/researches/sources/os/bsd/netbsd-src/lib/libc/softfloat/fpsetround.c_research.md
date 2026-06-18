# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetround.c

Read completely: 60 lines.

Implements `fpsetround(rnd_dir)`. It delegates to `set_float_rounding_mode` when available; otherwise it swaps `float_rounding_mode` and returns the previous value. Provides weak alias `_fpsetround`.

Risk: fallback path does not validate `rnd_dir`; invalid enum values would affect later SoftFloat rounding decisions.
