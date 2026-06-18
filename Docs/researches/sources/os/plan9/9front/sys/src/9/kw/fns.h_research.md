# File Research: sources/os/plan9/9front/sys/src/9/kw/fns.h

Kirkwood ARM platform function declarations and low-level helper macros. It combines imported port-layer prototypes with machine-specific assembly/C routines used across boot, MMU, traps, cache management, interrupts, process setup, UART, FPU emulation, and memory allocation.

Key exported areas include cache and L2-cache maintenance, CP15 register accessors, TLB operations, process save/restore hooks, interrupt registration, vector setup, MMU mapping helpers, uncached allocation, and early UART output. `coherence` is defined as `barriers`.

The file also defines `KADDR`, `PADDR`, `MASK`, PCI bus encoding helpers, and a `wave(c)` macro for emergency pre-console UART output through `PHYSCONS`.

Notable risks: comments explicitly say `KADDR`/`PADDR` are "not good enough"; the header is a broad platform contract and depends heavily on matching assembly symbol names.
