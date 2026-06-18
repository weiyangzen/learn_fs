# File Research: sources/os/plan9/9front/sys/src/cmd/5e/fpa.c

This file implements legacy ARM FPA floating-point emulation for `5e`.

Key routines:
- `resetfpa()` initializes `FPSR` to `0x81000000` and clears the first eight FP registers.
- `fpatransfer()` handles FPA memory transfers for float/double loads and stores with pre/post-indexing and writeback.
- `fpasecop()` maps encoded secondary operands to FP constants or FP registers.
- `fpaoperation()` implements arithmetic and unary FPA operations: add, multiply, subtract, reverse subtract, divide, reverse divide, move, negate, absolute, integer conversion, and sqrt, then stores at selected precision.
- `fparegtransfer()` transfers between ARM registers and FP registers/FPSR, and handles FP compare-to-CPSR when destination is R15.

Dependencies and interactions:
- Used by `arm.c:step()` for FPA instruction classes.
- Uses `P->F`, `P->FPSR`, `P->CPSR`, segment memory helpers, and `invalid()`.

Research relevance:
- Provides the non-VFP floating-point path selected by `5e -F`.

Risk notes:
- Only selected FPA operations are implemented; unknown opcodes fatal.
- FP compare sets ARM flags using host long-double comparisons, including unordered behavior through the final `else`.
- Transfers assume compatible host memory layout for float/double.
