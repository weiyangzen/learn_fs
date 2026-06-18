# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/arith.h

This gdtoa configuration header includes `<machine/endian.h>` and defines either `IEEE_BIG_ENDIAN` or `IEEE_LITTLE_ENDIAN` based on `BYTE_ORDER`. It tells David Gay dtoa/gdtoa code how floating-point words are arranged on MIPS.

Its correctness is essential for decimal/binary floating conversion. There are no functions or state.
