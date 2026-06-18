# File Research: sources/os/plan9/9front/sys/src/cmd/8c/cgen.c

This is the main 386 C expression and aggregate code generator.

Key responsibilities:
- `cgen()` lowers scalar expressions, assignments, calls, casts, comparisons, boolean expressions, pointer indirection, increments/decrements, bitfields, arithmetic, shifts, division, multiplication, and floating operations.
- Handles special x86 register constraints, especially `CX` for variable shifts and `AX`/`DX` for multiply/divide.
- Optimizes constant multiply/divide/modulo using helpers from `mul.c` and `div.c`.
- Delegates 64-bit/vlong operations to `cgen64()` when needed.
- `lcgen()` and `reglcgen()` compute lvalues and indirectable addresses.
- `boolgen()` lowers boolean control flow and optionally materializes boolean results.
- `sugen()` handles structure/union and 64-bit-sized copy/generation, including function returns and string-copy style aggregate moves.

Integration points:
- Emits `Prog` records via `gins()`, `gopcode()`, `fgopcode()`, `gmove()`, `gbranch()`, and `patch()` from `txt.c`.
- Uses addressability/complexity results from `sgen.c`.
- Uses bitfield helpers from `swt.c`, register allocation from `txt.c`, and 64-bit helpers from `cgen64.c`.

Risks and invariants:
- Correctness depends on balancing `regalloc()`/`regfree()` across many control-flow paths.
- Several paths temporarily reserve hard registers by incrementing `reg[]`.
- Complex subexpressions with function calls are rewritten into temporaries to preserve evaluation order.
