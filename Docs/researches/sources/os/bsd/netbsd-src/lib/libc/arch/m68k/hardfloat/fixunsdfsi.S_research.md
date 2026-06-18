# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fixunsdfsi.S

This helper implements double-to-unsigned-int conversion. It truncates toward zero, compares with `2147483648.0`, and for large values subtracts that threshold and sets bit 31 in the integer result; ColdFire uses a rodata constant.
