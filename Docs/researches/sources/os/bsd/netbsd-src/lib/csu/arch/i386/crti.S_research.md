# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/i386/crti.S

i386 `crti` fragment. It includes `sysident.S`, aligns `.init` and `.fini`, and defines `_init` / `_fini` prologues.

Each prologue saves `%ebp` and establishes a frame pointer.
