# File Research: sources/os/plan9/9front/sys/src/cmd/6c/cgen.c

This file is the amd64 backend expression and structure code generator for `6c`.

Key elements:
- `cgen()` emits code for scalar expressions, assignments, bitfields, unary ops, shifts, arithmetic/logical ops, multiplication/division/modulo, compound assignments, function calls, indirection, comparisons, boolean expressions, casts, field selection, conditionals, comma expressions, and pre/post increment/decrement.
- Handles evaluation order carefully when both sides may contain function calls (`complex >= FNX`) by spilling temporaries.
- Uses x86 architectural constraints:
  - variable shifts use `CX`,
  - division/modulo use `AX` and `DX`,
  - structure copies use `SI`, `DI`, and `CX`.
- Optimizes common constants:
  - zero add/sub cases,
  - shift-left-by-one as add,
  - multiply/add address forms via `genmuladd()`,
  - multiply/divide/modulo by constants through `mulgen()`, `sdiv2()`, `smod2()`, `sdivgen()`, and `udivgen()`.
- `reglcgen()` and `lcgen()` compute lvalue addresses, preserving constant offsets through indirection when possible.
- `bcgen()` and `boolgen()` generate branches or materialized boolean values.
- `sugen()` handles struct/union copies, struct literals, function-returned structs, conditional struct expressions, and block copy lowering.
- Small structure copies use scalar MOVL/MOVQ/MOVB loops; larger copies use `CLD; REP; MOVSL` plus optional byte tail copy.
- Utility functions include `layout()`, `immconst()`, `hardconst()`, `castup()`, `zeroregm()`, `vaddr()`, `hi64v()`, `lo64v()`, `hi64()`, `lo64()`, and `cond()`.

Dependencies and integration:
- Relies on backend helpers from `gc.h` and other `6c` files: register allocation, instruction emission, type tables, bitfield helpers, argument generation, branch patching, and opcode lowering.
- Calls division helper routines from `div.c`.

Notable behavior:
- The file has several historical comments marked “TO DO” and one disabled cast optimization block.
- It warns on pointer-to-shorter-integer casts.
- For comparisons involving floating point, relation mapping is adjusted through `logrel`/`invrel`.
- `vaddr()` determines whether a vlong source/destination can be accessed directly or needs address loading.

Research notes:
- This is a classic Plan 9 C backend: compact, direct, and strongly coupled to x86 register constraints.
