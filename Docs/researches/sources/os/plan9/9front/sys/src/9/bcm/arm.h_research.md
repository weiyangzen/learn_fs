# File Research: sources/os/plan9/9front/sys/src/9/bcm/arm.h

ARMv6/v7 status register, coprocessor, cache, MMU, and page-table definitions.

Key definitions:
- CPSR mode/interrupt/status bit masks.
- FPA/VFP coprocessor identifiers and instruction classification macros.
- CP15 register, CRm, op1/op2 constants for ID, control, timers, fault, cache, TLB, vectors, and performance monitor access.
- Main/auxiliary control register bits for ARMv6/v7.
- Cache and TLB operation encodings.
- Translation table cacheability bits.
- L1/L2 PTE type, cache, shareability, AP, DAC, and no-exec bits.
- High vector base constant.

Dependencies:
- Used by ARM assembly, MMU, trap, clock, coprocessor, and FPU code.

Research notes:
- Central compatibility header for both ARM1176 and Cortex-A7 style ports.
