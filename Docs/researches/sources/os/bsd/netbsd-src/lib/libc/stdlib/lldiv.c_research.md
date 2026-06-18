# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/lldiv.c

Read completely: 66 lines.

Implements `lldiv(long long int num, long long int denom)`. It follows the same quotient/remainder correction logic as `div.c` and `ldiv.c`.

Provides a libc weak alias for `_lldiv`.
