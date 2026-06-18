# File Research: sources/teaching/xv6-public/bootasm.S

First-stage boot assembly loaded by BIOS at physical `0x7c00`.

Key behavior:
- Starts in 16-bit real mode, disables interrupts, clears segment registers, and enables the A20 line.
- Installs a small bootstrap GDT with flat code/data descriptors.
- Sets `CR0_PE` and performs a far jump into 32-bit protected mode.
- Initializes protected-mode segment registers, sets the stack to `start`, and calls `bootmain`.
- If `bootmain` returns, writes Bochs breakpoint port values and spins.

Important interactions:
- Uses `asm.h`, `memlayout.h`, and `mmu.h`.
- Paired with `bootmain.c`; together they must fit in one signed boot sector.
