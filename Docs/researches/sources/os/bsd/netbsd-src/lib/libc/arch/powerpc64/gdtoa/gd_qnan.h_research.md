# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc64/gdtoa/gd_qnan.h

This header defines PowerPC64 gdtoa quiet-NaN constants. It sets the single-precision pattern to `0x7fc00000` and double words to `0x7ff80000, 0x0`.

The constants match the architecture’s big-endian IEEE layout and are used by conversion code that synthesizes NaN values.
