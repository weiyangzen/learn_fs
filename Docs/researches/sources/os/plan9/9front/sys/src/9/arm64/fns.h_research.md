# File Research: sources/os/plan9/9front/sys/src/9/arm64/fns.h

ARM64 architecture function declaration header.

Key declarations:
- Assembly helpers for interrupts, atomics, labels, user entry, FPU register save/restore, TLB operations, and hypercalls.
- Cache maintenance APIs from `cache.v8.s`.
- MMU mapping and process-ASID APIs.
- Boot, clock, FPU, trap, IRQ, PCI, UART, DMA, and configuration entry points.
- Stub-style prototypes for subsystems not present in this target but expected by shared code.

Dependencies:
- Extends `../port/portfns.h`.

Research notes:
- This header is the main contract between ARM64 C code and assembly support files.
