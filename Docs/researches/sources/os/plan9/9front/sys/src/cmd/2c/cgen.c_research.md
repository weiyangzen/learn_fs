# File Research: sources/os/plan9/9front/sys/src/cmd/2c/cgen.c

Purpose: expression-level code generator for the 68020 C compiler backend.

Key behavior:
- `cgen()` recursively lowers C expression trees into `Prog` instructions, respecting addability, register pressure, side effects, function-call complexity, bit-fields, and requested result location.
- Handles scalar assignments, compound assignments, bit-field assignment/update, casts, conditional expressions, indirection, function calls, arithmetic, logical ops, comparison-to-bool generation, comma expressions, address-of, unary ops, and pre/post increment/decrement.
- Uses `regalloc()`, `regaddr()`, `regpair()`, `regret()`, `regfree()`, `gmove()`, `gopcode()`, `gbranch()`, `patch()`, `doinc()`, and bit helpers from sibling files.
- Optimizes constant multiply/shift through `mulcon()`/`shlcon()`, folds some address arithmetic into stack/TOS addressing, and chooses evaluation order from node complexity.
- `lcgen()` computes lvalues/addresses; `bcgen()` and `boolgen()` produce branch or materialized boolean results.
- `sugen()` handles structure/union and wide-value generation, including copies, compound struct literals, function returns by hidden result pointer, and rathole temporaries.

Research notes:
- `D_TOS` is used as an evaluation spill/argument-stack location when both sides contain calls or when argument order requires stack preservation.
- Division/modulo use register pairs for integer results, with quotient/remainder selected from adjacent registers.
- Several code paths warn about “non-interruptable temporary” when using `nodrat` rathole storage.
