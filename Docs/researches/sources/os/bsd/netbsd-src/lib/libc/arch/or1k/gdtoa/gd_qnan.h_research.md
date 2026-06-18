# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/or1k/gdtoa/gd_qnan.h

This header defines or1k gdtoa quiet-NaN constants. It sets the single-precision NaN to `0x7fc00000` and the big-endian double words to `0x7ff80000, 0x0`.

It is used when gdtoa conversion code must synthesize NaNs. The constants match the architecture’s declared big-endian IEEE layout.
