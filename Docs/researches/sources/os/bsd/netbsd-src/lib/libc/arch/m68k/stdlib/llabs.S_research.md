# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/llabs.S

This file implements `_llabs` and weak aliases `llabs` and `imaxabs`. It loads a 64-bit signed integer into `%d0/%d1`, checks the sign in the high word, and if negative performs a two-word negation using `negl` and `negxl`.

It provides compiler/stdlib ABI support for `long long` and `intmax_t` absolute values on m68k. The implementation depends on m68k extended carry behavior for correct 64-bit negation.
