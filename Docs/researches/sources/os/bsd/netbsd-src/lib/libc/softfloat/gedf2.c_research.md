# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/gedf2.c

Read completely: 24 lines.

Defines `__gedf2` for double-precision greater-or-equal comparison. It implements the libgcc convention `(a >= b) - 1` as `float64_le(b, a) - 1`.

Risk: adapter relies on `float64_le` raising invalid for unordered NaN comparisons as required by the underlying SoftFloat semantics.
