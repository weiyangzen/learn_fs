# File Research: sources/os/plan9/9front/sys/src/9/kw/l.s

Kirkwood ARMv5/ARM926EJ-S boot and low-level assembly. `_start` is entered from U-Boot with the MMU disabled, switches to SVC mode, disables MMU/caches, flushes L1/L2, creates initial section mappings, enables the MMU/caches, warps execution into the virtual kernel mapping, clears the low identity map, sets the Mach stack, and calls `main`.

The file also contains an unused `_reset` path, emergency UART output helper, cache enable/disable and L1 cache maintenance routines, Marvell L2 cache control/flush/invalidate routines, MMU enable/disable/TLB invalidation, CP15 register accessors, interrupt priority routines (`spl*`), atomic/tas helpers, label save/restore, idle wait-for-interrupt, and barrier wrapper.

The initial page tables map low DRAM temporarily, map 512 MiB at `KZERO`, and map MMIO. Later C code refines vector and I/O mappings.

Notable risks: the code contains hardware-specific cache-flush loops and SheevaPlug L2 sequences; comments call out ARM/assembler ambiguities and deprecated `SWPW` use for tas.
