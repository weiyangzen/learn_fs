# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/hardfloat/flt_rounds.c

This m68k hardfloat routine implements `__flt_rounds` by reading the FPCR with `fmovel`, extracting `FPCR_ROUND`, and XORing with `1` to map hardware encoding to C `FLT_ROUNDS` semantics.
