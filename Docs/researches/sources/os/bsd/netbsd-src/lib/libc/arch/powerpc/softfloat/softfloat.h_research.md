# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/powerpc/softfloat/softfloat.h

This header declares the PowerPC SoftFloat API. It leaves `FLOATX80` and `FLOAT128` disabled, defines `float32` and `float64`, maps rounding and exception state to NetBSD IEEE FP constants, and declares conversion, arithmetic, comparison, and NaN-test routines.

The optional extended/quad blocks are present but inactive unless macros are changed. This file is nearly the same contract as or1k softfloat, adapted through `powerpc-gcc.h`.
