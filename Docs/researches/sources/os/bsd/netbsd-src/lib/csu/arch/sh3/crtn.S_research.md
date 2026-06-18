# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crtn.S

SH3 `crtn` fragment. It provides matching epilogues for `.init` and `.fini`.

The epilogue restores `sp` from `r14`, restores `pr`, returns with `rts`, and restores `r14` in the delay slot.
