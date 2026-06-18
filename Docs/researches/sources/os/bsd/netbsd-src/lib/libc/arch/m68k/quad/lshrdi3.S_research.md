# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/quad/lshrdi3.S

This file implements `__lshrdi3`, the unsigned/logical 64-bit right-shift helper for m68k. It moves bits from the high half into the low half for shifts under 32 and clears the high half for shifts of 32 or more.

It backs compiler-emitted unsigned `long long` shifts. The key distinction from `__ashrdi3` is zero-fill behavior, so regressions here would affect unsigned arithmetic and bit-manipulation code.
