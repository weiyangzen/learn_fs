# File Research: sources/os/plan9/9front/sys/src/9/arm64/mem.h

ARM64 memory layout, page-table, and PTE constant definitions.

Key definitions:
- Page size, effective virtual address width, page-table level math, and index macros.
- Kernel virtual layout for `VDRAM`, `KTZERO`, `KZERO`, `VMAP`, `KMAP`, `KSEG0`, and Mach areas.
- Boot argument, DTB, reboot trampoline, user text, stack, and user segment limits.
- Cache/memory attribute encodings, shareability, MAIR slots, and PTE bits.
- Physical DRAM base and utility macros.

Dependencies:
- Used by C and assembly across boot, MMU, traps, and devices.

Research notes:
- The effective VA width is 36 bits, with a high-half kernel layout.
- `KZERO` provides direct mapping for the first 1 GB of physical RAM.
