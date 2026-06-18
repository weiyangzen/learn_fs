# File Research: sources/os/plan9/9front/sys/src/9/lx2k/fns.h

LX2K ARM64 platform function declarations. It exposes low-level assembly routines for exceptions, atomics, interrupt priority, user entry, FPU control, SMC calls, TTBR/TLB maintenance, cache maintenance, MMU helpers, clock, trap/IRQ, UART, DMA flushing, PCI config/interrupts, and platform configuration.

The header defines `PADDR`/`KADDR` through platform functions rather than simple masks, and declares Plan 9 linkage points such as `trapinit`, `intrinit`, `mmu1init`, `putasid`, `meminit`, and `uartconsinit`.

Notable risks: declarations include broader SoC APIs (`ccm`, `gpc`, `iomux`, `gpio`, `lcd`) that are not implemented in this group, implying shared ARM64 platform expectations.
