# File Research: sources/os/plan9/9front/sys/src/9/ppc/fns.h

PowerPC machine function declarations and key address macros.

Key responsibilities:
- Includes shared `portfns.h` and declares PPC/board functions for clocking, traps, interrupts, MMU, cache maintenance, floating point, special registers, PCI, process switching, timers, and console/debug output.
- Defines `idlehands()` as empty, `userureg()`, `KADDR()`, `PADDR()`, and `coherence()`.
- Declares optional UCU-specific PLL/L2 helpers.

Dependencies:
- Prototypes match functions implemented across `l.s`, board files, `mmu.c`, `trap.c`, and other PPC kernel sources.

Notable behavior:
- Several duplicate prototypes are present, reflecting historical hand-maintained header style.
