# File Research: sources/os/plan9/plan9/sys/src/cmd/8c/cgen.c

## Purpose
Main expression and structure code generator for the Plan 9 386 C compiler backend.

## Key Functions
- `cgen()` emits scalar expression code into an optional destination node.
- `reglcgen()` computes an addressable lvalue through a temporary register.
- `lcgen()` emits address generation for lvalues.
- `bcgen()` and `boolgen()` generate conditional branches and boolean materialization.
- `sugen()` copies or builds aggregate values, including structures, 64-bit values, function returns, and conditional/comma aggregate expressions.

## Important Behavior
- Delegates structures/unions and 64-bit values to `sugen()` and `cgen64()`.
- Handles assignments, compound assignments, arithmetic, shifts, multiplication/division/modulus, calls, indirection, casts, conditionals, comma expressions, bitfields, and pre/post increment/decrement.
- Uses fixed x86 registers where required:
  - `CX` for variable shifts,
  - `AX/DX` for division and some multiplication forms.
- Optimizes constant multiplication/division/modulus through `mulgen()`, `sdiv2()`, `smod2()`, `sdivgen()`, and `udivgen()`.
- Uses x87 stack registers for floating-point operations via `fregnode0` and `fregnode1`.
- Emits block copies with `CLD; REP; MOVSL/MOVSB`.

## Research Notes
This is the core lowering pass from compiler IR nodes to abstract Plan 9 386 assembly.
