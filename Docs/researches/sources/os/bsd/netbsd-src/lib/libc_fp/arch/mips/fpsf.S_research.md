# File Research: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/fpsf.S

## Purpose
Implements single-precision GCC soft-float helper symbols using MIPS floating-point hardware instructions.

## Main Entry Points
Provides `__addsf3`, `__subsf3`, `__mulsf3`, `__divsf3`, `__negsf2`, double-to-single truncation, single-to-int conversions, unsigned conversions, int-to-single conversions, and comparison/unordered helpers.

## Control Flow
Integer-register float bit patterns are moved into FP registers, computed with `.s` FP instructions, and returned via integer registers. Unsigned conversion helpers use large FP constants and integer biasing.

## Dependencies
Depends on MIPS COP1, `<mips/asm.h>`, GCC soft-float helper symbol conventions, and MIPS ABI register conventions.

## Risks And Notes
Some strong aliases appear to point at double-named comparison helpers, so symbol naming must be checked against the assembler macro/ABI expectations when modifying this file.
