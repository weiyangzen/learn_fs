# File Research: sources/os/plan9/9front/sys/src/cmd/vc/cgen.c

Purpose: MIPS expression, boolean, lvalue, call, bitfield, and structure code generation for the Plan 9 C compiler backend.

Key behavior:
- `cgen` recursively lowers C expression trees into backend `Prog` instructions, handling assignments, arithmetic, calls, indirection, address generation, casts, conditionals, comma expressions, and pre/post increments.
- Handles hard evaluation order cases by saving complex function-call results into temporaries.
- Uses immediate forms for suitable constant arithmetic/logical operations.
- `genasop` handles compound assignments with careful lvalue address preservation.
- `reglcgen` and `lcgen` compute lvalue addresses, including constant-offset folding for indirect additions.
- `bcgen` and `boolgen` generate branches or boolean values for logical, comparison, constant, conditional, and short-circuit expressions.
- `sugen` copies or initializes structs/unions, rewrites side-effecting destinations, handles struct-return calls, and emits word-copy loops for larger objects.
- `layout` emits small unrolled word-copy sequences used by `sugen`.

Dependencies:
- Uses `gc.h` backend types, register allocators and instruction emitters from `txt.c`, bitfield helpers from `swt.c`, multiply optimization from `swt.c`/`mul.c`, and common compiler tree helpers.

Notable details:
- Structure copies are word-based and choose a small unroll factor before loop emission.
- Floating and integer boolean materialization paths differ: floating comparisons branch via FP compare instructions.
