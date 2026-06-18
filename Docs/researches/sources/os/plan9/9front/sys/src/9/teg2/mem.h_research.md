# File Research: sources/os/plan9/9front/sys/src/9/teg2/mem.h

Tegra 2 memory layout and MMU constants.

Purpose:
- Defines machine-wide sizes, alignment, kernel/user address layout, page constants, PTE flags, and physical/virtual MMIO regions.

Key definitions:
- 4 KiB pages, 32-byte cache lines, 4 CPUs max, 16 KiB kernel stacks, 1 GiB DRAM target.
- `KZERO`/`KSEG0` at `0xC0000000`, `KTZERO` at `KZERO+0x410000`, user space below roughly 1 GiB.
- Reserves high memory for vectors and L2 page tables through `RESRVDHIMEM`.
- Defines Tegra-specific regions for CPU MMIO, PL310 L2, exception vector peripheral, console UART, AHB, and NOR mappings.

Integration:
- Used by C and assembly, especially `l.s`, `mmu.c`, `trap.c`, and device drivers.

Risks/notes:
- Constants encode board-specific assumptions; changing DRAM size, vectors, or MMIO windows affects boot mappings and allocator boundaries.
