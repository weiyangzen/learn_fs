# File Research: sources/os/plan9/plan9/sys/src/9/omap/arm.h

Defines Cortex-A8/ARMv7 PSR, coprocessor, CP15, cache/TLB, and MMU page-table constants for C and assembly.

Key points:
- Defines ARM processor modes and interrupt-disable/status bits in CPSR/SPSR.
- Names coprocessors: VFP single/double (`CpFP`, `CpDFP`) and system control (`CpSC`/CP15).
- Defines CP15 primary registers for ID, control, TTB, DAC, fault status/address, cache ops, TLB ops, lockdown, vector base, PID, and Cortex-specific cache/TLB controls.
- Defines opcode fields for TTB0/TTB1/TTB control, DFSR/IFSR, cache-size selection, ID registers, and vector-base registers.
- Defines main control register bits such as MMU enable, alignment fault, D-cache/I-cache, branch prediction, high vectors, access flag, exception endian, and ARMv7 must-be-one/zero masks.
- Defines auxiliary control bits for cache/TLB maintenance behavior, L2 enable, speculative access, NEON/L1 behavior, and issue restrictions.
- Defines CP15 cache maintenance selectors for invalidate, writeback, writeback+invalidate, VA-to-PA, set/way, branch target cache, and barriers.
- Defines TLB invalidate selectors and lockdown selectors.
- Defines L1/L2 page-table encodings: fault, coarse, section, fine, large/small page, cached/buffered, domain, access permissions, and `HVECTORS`.

Dependencies and interactions:
- Included by OMAP C and assembly files including `arm.s`, `cache.v7.s`, `clock.c`, `coproc.c`, and MMU/trap code.
- Supplies bit definitions for dynamic CP15 instruction generation in `coproc.c`.

Research relevance:
- Core ARMv7 architectural definition file for the OMAP port.
