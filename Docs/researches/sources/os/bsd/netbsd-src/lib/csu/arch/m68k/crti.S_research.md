# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/m68k/crti.S

m68k `crti` fragment. It includes `sysident.S` and defines `_init` and `_fini` labels in aligned executable sections.

No explicit stack frame is created in this prologue.
