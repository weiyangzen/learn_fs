# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/imaxdiv.c

Read completely: 66 lines.

Implements `imaxdiv(intmax_t num, intmax_t denom)`. It computes quotient and remainder and applies the same correction used by `div.c` so the quotient truncates toward zero even on machines whose native signed division historically differed.

Provides a libc weak alias for `_imaxdiv`.
