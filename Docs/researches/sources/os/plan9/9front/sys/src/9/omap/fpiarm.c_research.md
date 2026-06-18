# File Research: sources/os/plan9/9front/sys/src/9/omap/fpiarm.c

ARM floating-point and selected atomic instruction emulator.

Key behavior:
- Decodes and emulates old ARM 7500 FPA instructions and VFP single/double operations when they trap as undefined instructions.
- Uses `fpi.c` and `fpimem.c` for arithmetic and conversion.
- Implements binary operations, unary operations, comparison/condition-code updates, loads/stores, and conversions to integer.
- `condok` applies ARM condition-code predicates from CPSR.
- `fpaemu` handles legacy FPA-style instruction encodings.
- `vfpemu` handles VFP register-transfer, arithmetic, load/store, and compare cases.
- `ldrex` and `strex` emulate exclusive access instructions using global `ldrexvalid` state.
- `casemu` emulates compare-and-swap style instruction patterns.
- `fpiarm` is the public trap-side entry point; it fetches the faulting instruction, dispatches emulation, and advances PC when handled.

Research notes:
- Header comments state it does not fully model ARM floating-point status/properties beyond what the Inferno-derived environment needs.
- All arithmetic is effectively done through the internal double-precision representation.
