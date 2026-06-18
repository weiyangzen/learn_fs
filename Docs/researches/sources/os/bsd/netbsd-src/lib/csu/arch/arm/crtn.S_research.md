# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/arm/crtn.S

ARM `crtn` fragment. It provides the matching epilogue for both `.init` and `.fini`.

The epilogue restores frame pointer, stack pointer, and program counter via `ldmea fp, {fp, sp, pc}`.
