# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtbegin.h

MIPS `crtbegin` architecture header. It injects constructor/destructor helper calls into `.init` and `.fini`.

The o32 ABI path manually sets `$gp`, resolves helpers through GOT entries, and uses explicit `R_MIPS_JALR` relocations; other ABI paths use direct `jal`.
