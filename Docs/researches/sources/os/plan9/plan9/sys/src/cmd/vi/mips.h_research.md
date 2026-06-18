# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/mips.h

Purpose: Shared declarations and machine model for the MIPS simulator/debugger.

Key behavior:
- Defines breakpoints, TLB, instruction cache, instruction table entries, register file, floating register formats, multiply results, segment/memory structures, opcode decode macros, constants, prototypes, and globals.
- Defines Plan 9/MIPS user address constants, stack layout constants, and instruction dispatch macro `Iexec`.

Dependencies:
- Includes Plan 9 MIPS `ureg.h` and relies on `mach` library types.

Notable details:
- The register file stores GPRs, HI/LO, FPSR, and a union view over double/float/integer FP registers.
