# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/gdtoa/arith.h

This gdtoa configuration header includes `<machine/endian.h>` and defines `IEEE_BIG_ENDIAN` or `IEEE_LITTLE_ENDIAN` based on `BYTE_ORDER`. SH3 supports endian variation, so gdtoa must be configured at compile time.

There is no runtime behavior. The file controls floating-point word interpretation in conversion code.
