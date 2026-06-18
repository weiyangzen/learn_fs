# File Research: sources/os/plan9/plan9/sys/src/9/bcm/fpiarm.c

Software emulator for old ARM FPA floating-point opcodes.

Key behavior:
- Emulates visible Inferno/Plan 9 FPA behavior using `Internal` floating-point arithmetic from `../port/fpi.h`.
- Supports old ARM 7500 FPA register model and constants.
- Implements arithmetic operations add/sub/reverse-sub/mul/div/reverse-div, unary move/neg/abs/round, comparisons, float/int conversions, FPSR/FPCR transfers, and single/double memory load/store.
- Decodes ARM conditional execution and advances `Ureg->pc` as if instructions executed.
- Initializes process FP state to `FPemu` on first emulated instruction.
- Stops when the current instruction is no longer an FPA coprocessor opcode.
- Unsupported/deprecated operations raise an error with PC/opcode context.

This is used from trap undefined-instruction handling via `fpuemu()` paths.
