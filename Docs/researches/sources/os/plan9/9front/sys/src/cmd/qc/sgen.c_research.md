# File Research: sources/os/plan9/9front/sys/src/cmd/qc/sgen.c

Pre-codegen AST simplification and addressability analysis for the Power C backend.

Key responsibilities:
- `noretval` emits artificial uses of integer/floating return registers to suppress incorrect unused-result assumptions.
- `xcom` computes node `addable` and `complex` values.
- Recognizes directly addressable constants, names, registers, indirect registers, address-of, dereference, and constant-offset additions.
- Rewrites multiplication/division/modulo by powers of two into shifts/ands.
- Simplifies shifts and invokes `com64` for 64-bit specific canonicalization.
- Normalizes immediate-friendly operations by moving constants to the right side.

Dependencies and coupling:
- Works with common compiler transformations (`vlog`, `simplifyshift`, `complex`) and `com64.c`.
- Its complexity values drive evaluation order in `cgen.c`.

Notable behavior:
- Uses `FNX` to mark function calls/expressions requiring special ordering.
