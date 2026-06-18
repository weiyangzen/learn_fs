# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/negxf2.c

Read completely: 27 lines.

Defines `__negxf2` for extended double-precision negation when `FLOATX80` is enabled. Instead of toggling the sign bit directly, it computes `__mulxf3(a, __floatsixf(-1))`.

Risk: unlike the other negation wrappers, this routes through multiplication and integer-to-extended conversion, so it can inherit arithmetic exception/NaN behavior rather than acting as a simple sign-bit toggle.
