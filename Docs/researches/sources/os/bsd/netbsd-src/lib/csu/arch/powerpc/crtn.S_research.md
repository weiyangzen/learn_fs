# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/powerpc/crtn.S

PowerPC `crtn` fragment. It restores the saved link register, releases the stack frame, and returns with `blr`.

Separate but identical-form epilogues are emitted for `.init` and `.fini`, with 32/64-bit frame differences.
