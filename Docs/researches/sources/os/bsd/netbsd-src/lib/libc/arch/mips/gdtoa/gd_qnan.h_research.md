# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/gdtoa/gd_qnan.h

This header defines canonical quiet-NaN bit patterns for MIPS gdtoa output. It sets `f_QNAN` and endian-dependent word ordering for double and long-double/quad patterns.

The constants are consumed by gdtoa conversion code when it needs to synthesize NaNs. The main risk is word-order mismatch, especially because MIPS supports both big- and little-endian configurations.
