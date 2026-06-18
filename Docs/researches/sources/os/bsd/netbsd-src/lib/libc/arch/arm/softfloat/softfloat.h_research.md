# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/softfloat.h

This is the ARM-local SoftFloat public interface header. It defines `float32` and `float64` storage types, optional extended/quad types, rounding mode and exception flag mappings to NetBSD `ieeefp.h`, and prototypes for integer conversions, single/double arithmetic, comparisons, quiet/signaling variants, and optional `floatx80`/`float128` routines. GCC-specific guards omit routines supplied by libgcc.
