# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/or1k/crti.S

OR1K `crti` fragment. It includes `sysident.S` for NetBSD ELF notes.

It emits no `.init` or `.fini` prologue because OR1K uses `.init_array` and `.fini_array`.
