# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/gdtoa/gd_qnan.h

This header defines PowerPC gdtoa quiet-NaN bit patterns. It sets single precision to `0x7fc00000` and big-endian double words to `0x7ff80000, 0x0`.

These constants are used when gdtoa must synthesize NaN values. They assume big-endian IEEE layout.
