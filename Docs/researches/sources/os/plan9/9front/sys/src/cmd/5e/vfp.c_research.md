# File Research: sources/os/plan9/9front/sys/src/cmd/5e/vfp.c

This file implements VFP floating-point emulation for `5e`.

Key routines:
- `resetvfp()` clears `FPSR` and all FP registers.
- `vfpregtransfer()` moves between ARM registers and VFP registers/FPSR; if reading FPSR into R15, it copies FPSR to CPSR.
- `vfprmtransfer()` handles VFP memory load/store of float or double values at aligned addresses.
- `vfparithop()` implements selected binary operations: multiply, add, subtract, and divide.
- `vfpotherop()` implements compare with zero/register, int-to-float, float-to-int, move, absolute, negate, and sqrt.
- `vfpoperation()` dispatches operation encodings to arithmetic or other operation handlers.

Dependencies and interactions:
- Called by `arm.c:step()` when VFP is enabled and instruction masks match.
- Uses `P->F`, `P->FPSR`, `P->CPSR`, memory helpers, and host `fabs()`/`sqrt()`.

Research relevance:
- Default floating-point path for `5e`.

Risk notes:
- Only a subset of VFP encodings is implemented; unsupported forms fatal.
- FP registers are stored as `long double`, but memory/register transfers treat them partly as float/double/int through casts.
- FPSR-to-CPSR transfer copies the whole FPSR, not only condition bits.
