# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/fpgetsticky.c

Read completely: 55 lines.

Implements `fpgetsticky()`, returning current software floating-point exception flags from `float_exception_flags`. Provides weak alias `_fpgetsticky`.

Risk: direct global-state read; concurrent or thread-local semantics are provided only by surrounding platform integration, not this file.
