# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/softfloat/arm-gcc.h

This SoftFloat platform header selects big or little endian from `__ARMEB__`, enables 64-bit integer support, defines SoftFloat integer typedefs, `LIT64`, and `INLINE`. Under `SOFTFLOAT_FOR_GCC`, it also defines `FLOAT64_DEMANGLE`/`FLOAT64_MANGLE`, swapping 64-bit words for legacy non-VFP little-endian FPA layout while leaving VFP and big-endian values unchanged.
