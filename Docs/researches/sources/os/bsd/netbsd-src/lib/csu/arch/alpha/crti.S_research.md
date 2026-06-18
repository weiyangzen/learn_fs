# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/alpha/crti.S

Alpha `crti` fragment. It includes NetBSD system identity notes and defines `_init` and `_fini` prologues.

Each prologue loads the global pointer, allocates a 32-byte stack frame, and saves return address and GP before later code is linked into the same section.
