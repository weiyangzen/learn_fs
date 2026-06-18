# File Research: sources/os/plan9/9front/sys/src/cmd/tc/cgen.c

Implements expression, address, boolean, and structure code generation for the 9front Thumb C compiler backend.

Key points:
- `cgen` is the main expression generator. It handles assignments, bitfields, arithmetic/logical operations, division/modulo optimizations, compound assignments, calls, indirection, comparisons, casts, comma/conditional expressions, and pre/post increment/decrement.
- Constant power-of-two signed division/modulo is lowered into shifts/masks with sign correction.
- Multiplication by constants delegates to `mulcon`.
- `reglcgen`, `reglpcgen`, and `lcgen` generate l-values/addresses, folding small constant offsets into indirect-register addressing where possible.
- `bcgen` and `boolgen` generate branches or boolean materialization for comparisons, constants, logical operators, conditionals, and generic truth tests.
- `sugen` copies or constructs aggregate and 64-bit-like values, including struct literals, struct assignment, function-returned structs, conditional structs, and block copies using `MOVM` where profitable.

Dependencies and interactions:
- Uses register allocation and instruction emission from `txt.c`.
- Uses bitfield helpers, switch/string/global helpers from `swt.c`, multiply table logic from `mul.c`, and type/complextity analysis from `sgen.c`.
- Relies on shared backend globals declared in `gc.h`.

Research relevance:
- This is the core lowering layer from C AST nodes to Thumb backend instructions.
