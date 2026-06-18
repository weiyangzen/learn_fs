# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/mips/crtn.S

MIPS `crtn` fragment. It restores the saved return address and ABI-dependent saved register state, releases the call frame, and returns.

Separate `.init` and `.fini` epilogues are emitted.
