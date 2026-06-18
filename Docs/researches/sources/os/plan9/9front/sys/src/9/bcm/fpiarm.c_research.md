# File Research: sources/os/plan9/9front/sys/src/9/bcm/fpiarm.c

ARM floating-point instruction emulator for FPA and VFP opcodes.

Key behavior:
- Uses Inferno internal FP routines for arithmetic, conversion, comparison, and rounding.
- Emulates ARM 7500 FPA load/store, transfer, compare, unary, and binary operations.
- Emulates selected VFP load/store, core/extension register transfer, data processing, compare, immediate, and conversion operations.
- Maintains emulated FP state in `FPalloc`, initializes constants/status, and handles notify duplication.
- Checks ARM condition codes before executing an FP instruction.
- Advances PC by 4 for each emulated FP instruction and stops at the first non-FP opcode.
- Raises errors for unimplemented FP instructions.

Dependencies:
- Uses `ureg.h`, `arm.h`, `../omap/fpi.h`, process FPU save state, and user address validation.

Research notes:
- Arithmetic is done in double precision and does not fully model ARM FP trap status.
