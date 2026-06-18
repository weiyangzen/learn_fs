# File Research: sources/os/plan9/9front/sys/src/9/omap/rebootcode.s

OMAP reboot trampoline copied to low memory during kernel reboot.

Key behavior:
- Disables interrupts, adjusts Cortex-A8 auxiliary control to reduce speculation/cache-maintenance risk, and turns caches off.
- Reworks double mappings so physical DRAM and kernel virtual addresses remain reachable during MMU shutdown.
- Switches execution, stack, and SB into physical DRAM space.
- Disables MMU and caches, copies the new kernel image from source to destination with `memmove`, flushes caches, and branches to the physical entry.
- Provides `cachesoff`, `_r15warp`, and stub `panic`/`pczeroseg`.
- Includes `cache.v7.s`.

Research notes:
- Comments state the code must fit under 11 KB to avoid stepping on PTEs.
- Serial wave characters trace reboot progress.
