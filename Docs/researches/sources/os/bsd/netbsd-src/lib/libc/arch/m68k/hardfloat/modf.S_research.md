# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/modf.S

This m68k FPU `modf` implementation splits a double into integer and fractional parts. It truncates the input toward zero, stores the integer part through the caller pointer, subtracts it from the original value, and returns the fractional part.
