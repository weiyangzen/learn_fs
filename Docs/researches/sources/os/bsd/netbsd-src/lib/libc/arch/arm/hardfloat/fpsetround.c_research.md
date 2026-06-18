# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetround.c

This routine reads the VFP `fpscr`, extracts and returns the old rounding mode, updates only `VFP_FPSCR_RMODE` with the requested `fp_rnd`, and writes the register back. It shares the same rounding encoding assertions as `fpgetround.c`.
