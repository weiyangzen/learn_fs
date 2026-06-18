# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpsetmask.S

This routine sets the VFP exception enable mask in `fpscr`. It preserves unrelated control bits, writes the new enable bits shifted into `VFP_FPSCR_ESUM`, and returns the previous mask.
