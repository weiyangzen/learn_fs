# File Research: sources/os/plan9/9front/sys/src/cmd/kc/cgen.c

Main expression and structure code generator for the SPARC C compiler backend. `cgen` handles scalar expression lowering: assignment, arithmetic, compound assignment, function calls, indirection, comparisons, boolean operators, casts, conditional expressions, and pre/post increment. It coordinates evaluation order using node complexity, allocates temporary registers, preserves function-call results through stack temporaries when needed, and delegates bitfields and structures to helper paths.

`boolgen` emits compare/branch sequences and optional materialized boolean values. `lcgen`/`reglcgen` compute l-values and fold small constant offsets into indirect references. `sugen` copies structures/unions, handles struct literals and function-returned aggregates, and emits looped or unrolled longword copies through `layout`. This file is central to SPARC-specific C AST-to-`Prog` lowering.
