# File Research: sources/os/bsd/netbsd-src/lib/csu/arch/riscv/crt0.S

RISC-V process entry stub. It initializes `gp` from `__global_pointer$` with relaxation disabled and jumps to common `___start`.

It also defines `_start_setgp`, places it in `.preinit_array`, and uses it to reset `gp` before early preinit processing.
