# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/cgen.c

Purpose: PowerPC C compiler expression/code generator for Plan 9 `qc`.

Key behavior:
- `cgen` lowers scalar expressions, assignments, bitfields, arithmetic/logical ops, compound assignments, calls, indirection, comparisons, boolean ops, comma, casts, struct field access, conditionals, and pre/post inc/dec.
- Chooses evaluation order based on expression complexity and function-call risk.
- Uses register allocators, address generators, and `gopcode`/`gmove` to emit target operations.
- Handles bitfield load/store through `bitload`/`bitstore`.
- `lcgen` and `reglcgen` produce l-values/addresses.
- `boolgen` and `bcgen` generate branch-based boolean evaluation and materialized boolean values.
- `sugen` copies/constructs structs/unions, rewrites struct literals, handles struct-return functions, and emits unrolled/looped long-word copies.
- `layout` emits small copy layouts using temporary registers.
- 64-bit support uses `isvdirect`, `isvconstable`, `vcgen`, `cmpv`, `testv`, and `cgen64` for `vlong` constants, casts, calls, and comparisons.

Dependencies and integration:
- Includes `gc.h`.
- Relies on compiler front-end node/type metadata, register allocation, instruction selection, branch patching, switch/bitfield helpers, and 64-bit helpers.

Risks and notes:
- Many comments identify old compromises, especially struct temporaries and vlong casts.
- 64-bit non-vlong conversion comments note typefd correctness gaps.
- Evaluation order is carefully tuned around function calls and side effects.
