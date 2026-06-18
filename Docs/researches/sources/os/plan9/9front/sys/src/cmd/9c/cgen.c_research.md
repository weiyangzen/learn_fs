# File Research: sources/os/plan9/9front/sys/src/cmd/9c/cgen.c

Main expression, boolean, lvalue, and aggregate code generator for the PowerPC64 C compiler backend.

Key functions:
- `cgen` lowers scalar AST nodes into backend instructions, handling assignments, bitfields, arithmetic/logical/shift operations, compound assignments, address/indirection, calls, comparisons, casts, comma/conditional expressions, and pre/post increment/decrement.
- Uses PowerPC-friendly immediate paths: signed 16-bit forms for add/sub and unsigned 16-bit/high-half forms for logical/shift-like operations.
- Converts `x ^ -1` to complement and delegates constant multiply optimization to `mulcon`.
- Handles function calls with argument generation, indirect-call temporaries, and return register moves.
- `reglcgen` and `lcgen` generate lvalue addresses, folding constant offsets into indirect operands when possible.
- `boolgen` and `bcgen` lower boolean expressions and comparisons into branches or materialized `0/1`.
- `sugen` handles structures/unions/vlong aggregates, struct literals, assignment, function returns through hidden pointers, conditionals, comma expressions, and rathole temporaries.
- `layout` copies aggregate words with small unrolled sequences or counted loops.

Filesystem relevance: indirect. It is compiler backend code used to build filesystem and OS components, not filesystem implementation.
