# File Research: sources/os/plan9/plan9/sys/src/9/bcm/arm.h

ARMv6 register, instruction-decoding, coprocessor, cache/TLB, MMU, and page-table constant header shared by C and assembly.

Key contents:
- Defines CPSR mode and flag bits (`PsrMusr`, `PsrMsvc`, `PsrDirq`, `PsrDfiq`, `PsrN/Z/C/V`).
- Defines coprocessor IDs and CP15 register/opcode names for system control, TTB, DAC, FSR/FAR, cache, TLB, vectors, and performance monitor access.
- Provides instruction classifiers for old FPA and VFP opcodes (`ISFPAOP`, `ISVFPOP`).
- Defines CP15 control bits for MMU, caches, prediction, high vectors, alignment, endianness, and ARMv7-reserved/must-be values.
- Defines cache/TLB maintenance opcode fields used by assembly helpers.
- Defines ARM section/coarse/small page descriptor bits, access permissions, DAC bits, and high-vector address `HVECTORS`.

This file is foundational for `l.s`, `lexception.s`, `mmu.c`, `trap.c`, `fpiarm.c`, and reboot code.
