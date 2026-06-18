# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/mips/softfloat/softfloat.h

This header declares the MIPS SoftFloat API. It leaves `FLOATX80` disabled, enables `FLOAT128` for `__mips_n32` and `__mips_n64`, defines `float32`, `float64`, optional `floatx80`, and `float128`, and maps rounding/exception state to NetBSD machine IEEE FP types.

It declares conversion and arithmetic routines for float32, float64, optional extended precision, and optional float128. Several declarations are conditional for `SOFTFLOAT_FOR_GCC` and `SOFTFLOAT_NEED_FIXUNS`, because some integer conversions are supplied by libgcc instead.

This header is both a libc API contract and compiler-runtime interface. ABI selection controls whether quad precision exists, making the MIPS64/o32 distinction important.
