# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crti.S

MIPS `crti` fragment. It includes NetBSD ELF identity notes and defines `_init` / `_fini` prologues with MIPS call frames.

The prologues set up GP, allocate `CALLFRAME_SIZ`, save `ra`, and preserve `s0` or GP depending on ABI.
