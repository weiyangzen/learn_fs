# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/ldiv.c

Read completely: 60 lines.

Implements `ldiv(long num, long denom)`. It mirrors `div.c`: compute native quotient/remainder, then adjust if needed to guarantee truncation toward zero.

Returns an `ldiv_t` with corrected `quot` and `rem`.
