# File Research: sources/os/plan9/9front/sys/src/cmd/7c/cgen.c

Expression and aggregate code generator for the ARM64 Plan 9 C compiler backend. It lowers C AST nodes into backend `Prog` instructions via `gopcode`, `gmove`, branches, register allocation helpers, switch/bitfield helpers, and structure-copy code.

Key functions:
- `cgen`/`cgenrel` handle scalar expression generation, including assignments, arithmetic, shifts, calls, indirection, address taking, casts, conditionals, pre/post increment/decrement, logical operators, and bitfield assignment paths.
- The generator uses node complexity and `FNX` to decide when to evaluate function-call-heavy subexpressions into temporaries before continuing.
- Arithmetic has special cases for immediates, power-of-two signed division/modulo, and constant multiplication via `mulcon`.
- `reglcgen` and `lcgen` generate lvalues/addresses, including offset folding when `usableoffset` says ARM64 addressing can represent the displacement.
- `boolgen` and `bcgen` lower comparisons and boolean expressions into branch sequences or materialized `0/1` results.
- `sugen` emits structure/union and vlong aggregate movement, including structure literals, function returns through hidden pointers, conditional aggregate expressions, and explicit copy loops.
- `layout` unrolls small structure copies and seeds loop counters for larger copies.
- `castup`, `hardconst`, and `cond` provide cast and predicate classification helpers.

Important interactions:
- Depends heavily on `txt.c` for instruction emission and register management.
- Calls `bitload`/`bitstore`, `mulcon`, `sugen`, `nullwarn`, `regsalloc`, and `regaalloc`.
- Mutates AST nodes in narrow cases to simplify lvalue and offset generation.

Filesystem relevance: indirect compiler backend infrastructure.
