# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/cmpdf2.S

This helper implements `__cmpdf2` for double comparison, returning `1` for greater-than, `-1` for less-than, and `0` for equality. ColdFire uses an explicit equality branch; other m68k FPU targets use condition-code-to-byte logic.
