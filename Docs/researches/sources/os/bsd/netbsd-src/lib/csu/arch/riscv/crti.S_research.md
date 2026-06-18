# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crti.S

RISC-V `crti` fragment. It includes NetBSD identity notes through `sysident.S`.

No `.init` / `.fini` prologue is emitted because NetBSD RISC-V uses `.init_array` and `.fini_array`.
