# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/cgen.c

This is the main expression and aggregate code generator for the SPARC C compiler backend. It lowers compiler AST `Node`s into backend `Prog` instructions through `gopcode()`, `gmove()`, and register allocation helpers.

`cgen()` handles scalar expressions, assignments, compound assignments, arithmetic/logical ops, shifts, multiplication/division/modulo, function calls, indirection, address generation, comparisons, boolean operators, casts, comma expressions, conditional expressions, increments/decrements, and bitfields.

`lcgen()` and `reglcgen()` compute lvalues and addresses, including indirection, conditional lvalues, and optimized constant-offset addressing. `boolgen()` emits branch-based boolean code with short-circuit handling and optional materialization into a target register.

`sugen()` handles structures/unions and wide constants. It emits fieldwise aggregate initialization, function-returned structures via hidden destination pointers, rathole temporaries for complex cases, and word-copy loops or unrolled copies. `layout()` performs the word move scheduling used by aggregate copies.

The file is central to correctness for C expression semantics. It relies heavily on the prior addressability/complexity pass and uses Plan 9 compiler conventions such as `nodrat`, `.safe`, and SPARC register-return rules.
