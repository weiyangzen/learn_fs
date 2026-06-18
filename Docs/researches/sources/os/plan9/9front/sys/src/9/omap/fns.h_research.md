# File Research: sources/os/plan9/9front/sys/src/9/omap/fns.h

Function prototypes and port macros for the OMAP kernel.

Key contents:
- Prototypes for architecture reset, clock, cache, MMU, DMA, trap, IRQ, UART, screen, coprocessor, FPU, and reboot helpers.
- Generic interrupt macros mapping `intrenable`/`intrdisable` to `irqenable`/`irqdisable`.
- Atomic-operation macros mapping Plan 9 CAS/TAS names to 32-bit ARM implementations.
- Address conversion macros `KADDR` and `PADDR`.
- `MASK(v)` bit-mask helper used heavily across the OMAP port.
- Stub macros for unsupported or trivial page-color/kmap behavior.

Research notes:
- This header is the main cross-file contract for the OMAP kernel subtree.
