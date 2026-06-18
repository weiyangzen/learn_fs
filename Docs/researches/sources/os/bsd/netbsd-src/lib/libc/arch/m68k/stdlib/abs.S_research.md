# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/stdlib/abs.S

This assembly file implements both `labs` and `abs`, with `labs` falling through into the `abs` entry. It loads the 32-bit argument from the stack into `%d0`, branches if nonnegative, otherwise negates it, and returns.

It is a compact machine-specific stdlib routine. Like standard C `abs`, the most negative two’s-complement value remains an overflow edge case; this file does not add special handling.
