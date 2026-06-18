# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/scon.c

This file performs constant folding and additive expression normalization.

Key behavior:
- `evconst()` folds unary, binary arithmetic, bitwise, relational, logical, cast, divide, and modulo expressions when operands are constant.
- `acom()` identifies additive/multiplicative-by-constant expressions suitable for normalization.
- `acom1()` flattens additive terms into multiplier/node terms.
- `acom2()` combines constants, factors common multipliers, reorders terms, and rebuilds a simplified expression tree.
- `addo()` decides whether a node is eligible for additive normalization.

Important details:
- Divide/modulo by zero are warned and not folded.
- Integer fold results are converted back through `convvtox()` for the target type.
- The additive optimizer avoids floating-point and unsupported vlong/pointer-width cases.
- Constants may be combined with address terms to improve address generation.

Filesystem relevance:
- Indirect compiler optimization support.
