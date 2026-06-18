# File Research: sources/os/bsd/netbsd-src/lib/libc_fp/arch/mips/fpdf.S

## Purpose
Implements double-precision GCC soft-float helper symbols using MIPS floating-point hardware instructions.

## Main Entry Points
Provides arithmetic helpers `__adddf3`, `__subdf3`, `__muldf3`, `__divdf3`, negation, single-to-double extension, double-to-int conversions, unsigned conversions, int-to-double conversions, and comparison/unordered helpers with strong aliases for GCC comparison entry points.

## Control Flow
Arguments are moved from integer registers to FP registers with `dmtc1`/`mtc1`, operations execute using `.d` FP instructions, and results are moved back to integer return registers. Unsigned conversions use subtract/add bias constants for the high signed range.

## Dependencies
Depends on MIPS assembler macros from `<mips/asm.h>`, COP1 FP instructions, MIPS ABI register conventions, and optional `MIPS3` synchronization nops.

## Risks And Notes
Correctness is ABI- and endianness-sensitive. Comparison helpers must return the exact values GCC expects for soft-float runtime calls, including unordered cases.
