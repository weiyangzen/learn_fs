# File Research: sources/os/plan9/9front/sys/src/9/omap/arm.s

Assembler macro include for the OMAP Cortex-A8 port.

Key contents:
- Kernel/physical address conversion and L1 page-table index macros.
- Section PTE templates for cached DRAM and uncached I/O.
- Delay and UART “wave” debug-output macros.
- Encodings for ARMv7 instructions not natively named by the assembler: SMC, WFI, DMB, DSB, ISB, CLZ, CPSIE/CPSID, VFP register moves.
- Cache/TLB barrier macros and page-table fill/zero helpers used by boot and reboot assembly.

Research notes:
- This file is macro infrastructure, not standalone executable code.
- It is included by `l.s`, `lexception.s`, and `rebootcode.s`.
