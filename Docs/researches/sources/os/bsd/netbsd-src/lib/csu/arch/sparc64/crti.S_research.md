# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/sparc64/crti.S

SPARC64 `crti` fragment. It includes NetBSD ELF identity notes and defines `_init` / `_fini` prologues.

Each prologue saves a larger 176-byte register-window frame, matching 64-bit SPARC ABI expectations.
