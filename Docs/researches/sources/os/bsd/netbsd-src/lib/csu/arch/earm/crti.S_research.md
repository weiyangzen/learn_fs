# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/earm/crti.S

EABI ARM `crti` fragment. It includes `sysident.S` for NetBSD ELF notes.

No `.init` / `.fini` prologue is emitted because ARM EABI uses `.init_array` and `.fini_array`.
