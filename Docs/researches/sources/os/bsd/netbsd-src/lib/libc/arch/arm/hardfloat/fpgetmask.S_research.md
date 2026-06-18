# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/arm/hardfloat/fpgetmask.S

This VFP-only fenv routine reads `fpscr` with `vmrs`, shifts exception enable bits down, masks them with `VFP_FPSCR_CSUM`, and returns the current floating-point exception mask. It provides weak aliasing from `fpgetmask` to `_fpgetmask` when enabled.
