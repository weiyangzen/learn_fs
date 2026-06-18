# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/sh3/gdtoa/gd_qnan.h

This header defines SH3 gdtoa quiet-NaN constants. It sets `f_QNAN` to `0x7fa00000` and chooses double-word order based on `BYTE_ORDER`.

These constants are used by gdtoa when generating NaN values. The endian conditional is the important architecture-specific detail.
