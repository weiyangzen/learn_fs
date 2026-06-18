# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/cgen.c

Main expression and aggregate code generator for the ARM C compiler backend `5c`.

Key behavior:
- `cgen`/`cgenrel` lower C expression trees to backend `Prog` instructions.
- Handles assignments, bitfields, arithmetic, division/modulo by powers of two, multiply optimization, compound assignments, address-of, calls, indirect loads, comparisons, logical ops, casts, comma, conditionals, and pre/post increments.
- `lcgen` and `reglcgen` compute lvalue addresses, including optimized small offsets.
- `boolgen` lowers boolean expressions and branches, including short-circuit logic and relational comparisons.
- `sugen` copies structures/unions and handles aggregate constants, structure literals, function-return aggregates, conditional aggregates, and multiword copy loops.

Notes:
- Carefully orders evaluation when both sides have function-call complexity.
- Uses ARM multi-register moves for small or looped structure copies.
