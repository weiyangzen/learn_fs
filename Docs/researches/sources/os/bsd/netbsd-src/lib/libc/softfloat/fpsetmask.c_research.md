# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetmask.c

Read completely: 60 lines.

Implements `fpsetmask(mask)`. If `set_float_exception_mask` is defined, it delegates to that hook; otherwise it stores `mask` in `float_exception_mask` and returns the old mask. Provides weak alias `_fpsetmask`.

Risk: accepts the mask as-is; any validation or hardware synchronization must happen in the optional hook.
