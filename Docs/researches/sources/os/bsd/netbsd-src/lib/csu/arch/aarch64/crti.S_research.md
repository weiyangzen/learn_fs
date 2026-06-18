# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/aarch64/crti.S

AArch64 `crti` startup fragment. It includes `sysident.S` so linked binaries receive NetBSD ELF notes.

The file intentionally has no `.init` / `.fini` prologue because AArch64 uses `.init_array` and `.fini_array`.
