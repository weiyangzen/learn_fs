# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sh3/crti.S

SH3 `crti` fragment. It includes `sysident.S` and defines `_init` / `_fini` prologues.

The prologue saves `r14` and `pr`, then establishes `r14` as a frame pointer.
