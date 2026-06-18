# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/hppa/crti.S

HPPA `crti` fragment. It includes NetBSD ELF identity notes and defines a macro that emits section prologues.

The prologue saves return pointer and stack frame state using HPPA frame constants, then instantiates `_init` and `_fini`.
