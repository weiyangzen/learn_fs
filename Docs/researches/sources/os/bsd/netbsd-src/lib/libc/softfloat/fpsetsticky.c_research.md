# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpsetsticky.c

Read completely: 60 lines.

Implements `fpsetsticky(except)`. It delegates to `set_float_exception_flags(except, 1)` when available; otherwise it replaces `float_exception_flags` and returns the old flags. Provides weak alias `_fpsetsticky`.

Risk: fallback path overwrites all sticky flags rather than merging; this matches the API but is important for callers clearing flags.
