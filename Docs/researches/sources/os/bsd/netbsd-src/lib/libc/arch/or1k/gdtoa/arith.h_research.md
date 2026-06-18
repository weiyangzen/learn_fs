# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/gdtoa/arith.h

This gdtoa configuration header declares `IEEE_BIG_ENDIAN` unconditionally for or1k. It tells gdtoa code to use big-endian floating-point word ordering.

There are no functions or state. Its correctness depends on the port’s ABI remaining big-endian for the supported configuration.
