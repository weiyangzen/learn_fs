# File Research: sources/os/plan9/9front/sys/src/cmd/cc/scon.c

Constant evaluation and additive expression reassociation for the Plan 9 C compiler.

Key behavior:
- `evconst` folds constant unary, binary arithmetic, logical, comparison, bitwise, cast, and shift operations.
- Emits warnings for divide/modulo by zero and float overflow/truncation paths handled elsewhere.
- `acom` rewrites integer additive/multiplicative expression trees into better grouped forms when safe.
- `acom1` decomposes additive expressions into coefficient terms plus constant.
- `acom2` factors and rebuilds expression trees, including constant-plus-address forms and coefficient factoring.
- `acast` inserts casts when reconstructed terms need target type conversion.
- `addo` decides whether an expression can safely participate in additive reassociation without changing overflow or unsigned semantics.

Dependencies:
- Includes `cc.h`.
- Uses compiler global `term`/`nterm`, type classification tables, `convvtox`, AST constructors, and diagnostics.

Research notes:
- Optimization is conservative around floating-point, vlong width, unsigned casts, and bit-field casts.
- This is source-tree-level expression simplification before machine-specific generation.
