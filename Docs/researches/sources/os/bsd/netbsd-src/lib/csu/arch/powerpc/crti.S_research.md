# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crti.S

PowerPC `crti` fragment. It includes `sysident.S` and defines `_init` / `_fini` prologues.

The prologue saves link register and allocates a stack frame, using different frame layouts for `_LP64` and 32-bit builds.
