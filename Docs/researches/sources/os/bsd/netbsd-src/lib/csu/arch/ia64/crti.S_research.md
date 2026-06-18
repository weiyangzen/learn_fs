# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/ia64/crti.S

IA-64 `crti` fragment. It includes NetBSD identity notes and defines `_init` and `_fini` prologues.

Each prologue aligns the section, allocates local registers, saves `ar.pfs`, and stores the return branch register in `loc0`.
