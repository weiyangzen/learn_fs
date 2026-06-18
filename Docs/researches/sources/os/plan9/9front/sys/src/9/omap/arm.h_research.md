# File Research: sources/os/plan9/9front/sys/src/9/omap/arm.h

Cortex-A8/ARMv7 definitions shared by C and assembly code in the OMAP port.

Key contents:
- ARM PSR mode, interrupt disable, and condition flag constants.
- Coprocessor numbers and CP15 register/opcode names for system control, cache, TLB, vectors, performance counters, and lockdown registers.
- Main control and auxiliary control bit definitions for MMU, caches, branch prediction, high vectors, access flags, and L2 behavior.
- ARM MMU descriptor constants for section/page entries, access permissions, domains, cacheability, and high vectors.
- Instruction classification macros for FPA/VFP coprocessor instruction decoding.

Research notes:
- This header is foundational for `l.s`, `cache.v7.s`, `lexception.s`, `coproc.c`, `trap.c`, `mmu.c`, and FPU emulation.
- The MMU constants are ARMv7-specific in places, with comments noting deprecated ARM access-permission encodings.
