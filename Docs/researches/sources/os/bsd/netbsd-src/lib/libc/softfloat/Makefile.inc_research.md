# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/Makefile.inc

This makefile fragment wires softfloat into libc.

It defaults `SOFTFLOAT_BITS` to 64 and sets `.PATH` to architecture-specific softfloat files plus `${.CURDIR}/softfloat/bits${SOFTFLOAT_BITS}` and the common softfloat directory. It adds architecture/common include directories, defines `SOFTFLOAT_FOR_GCC`, starts `SRCS.softfloat` with `softfloat.c`, and includes `softfloat/Makefile.fenv.inc` for rounding/mask/sticky accessors.

For ARM EABI machine arches it adds AEABI comparison helper sources. For other architectures it adds GCC-style comparison/negation/unordered helper sources for single, double, quad, and extended formats as applicable. It always adds `flt_rounds.c` and then appends `SRCS.softfloat` to `SRCS`.

There is also a GCC-specific warning suppression for MIPS and SH3 softfloat builds, disabling `-Wenum-compare` for `softfloat.c`.

Research notes and risks:
- `SOFTFLOAT_BITS` selects between bits32 and bits64 implementations; the listed group researches the bits32 implementation, but the default here is bits64 unless overridden by architecture make context.
- Source selection is ABI-sensitive, especially ARM EABI comparison helpers versus generic libgcc-style helpers.
