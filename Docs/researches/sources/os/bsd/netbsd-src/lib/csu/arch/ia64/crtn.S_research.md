# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crtn.S

IA-64 `crtn` fragment. It supplies the matching `.init` and `.fini` epilogues.

The epilogue restores `b0` and `ar.pfs`, then returns via `br.ret.sptk.many b0`.
