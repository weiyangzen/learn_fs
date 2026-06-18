# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crti.S

ARM `crti` fragment. It includes NetBSD ELF identity notes and defines `_init` and `_fini` prologues.

The prologue establishes an ARM frame by saving `{fp, ip, lr, pc}` and setting `fp`, so later linked section code can run with a normal frame.
