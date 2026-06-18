# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/com.c

Semantic typing and tree simplification pass for the Plan 9 C compiler. `complex` drives the sequence: type/lvalue checking (`tcom`/`tcomo`), comma hoisting, canonical simplification (`ccom`), constant evaluation (`acom`), machine-specific 64-bit/helper rewrites, and final machine expression complexity (`xcom`).

`tcomo` handles every major AST operator: assignments, arithmetic, shifts, comparisons, logical ops, casts, return, function calls/prototypes, names, string literals, struct member access, address/indirection, `sizeof`, `signof`, and structure constructors. It inserts casts, performs type compatibility checks, marks lvalues, diagnoses invalid operations, and performs array/function address decay when requested.

Later helpers validate function argument lists, resolve struct fields, validate structure constructors, hoist comma expressions out of subtrees, simplify address/indirection and arithmetic identities, fold constants, warn about divide-by-zero/stupid shifts, and diagnose useless or misleading comparisons using 128-bit range modeling.
