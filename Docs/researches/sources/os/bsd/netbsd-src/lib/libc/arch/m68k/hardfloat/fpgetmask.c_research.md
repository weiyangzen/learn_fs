# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/fpgetmask.c

This fenv routine reads the m68k FPCR and returns the exception enable mask extracted from `FPCR_EXCP2`. It weakly aliases `fpgetmask` to `_fpgetmask`.
