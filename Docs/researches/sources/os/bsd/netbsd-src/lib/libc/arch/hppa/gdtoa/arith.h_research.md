# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/hppa/gdtoa/arith.h

This gdtoa arithmetic header declares `IEEE_BIG_ENDIAN` for HPPA. It informs generic conversion code that floating-point words use big-endian layout.

The file is tiny but important for correct decimal conversion and NaN word ordering.
