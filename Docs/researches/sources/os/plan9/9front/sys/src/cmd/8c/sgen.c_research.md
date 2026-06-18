# File Research: sources/os/plan9/9front/sys/src/cmd/8c/sgen.c

This file computes expression complexity and addressability for the 386 backend.

Key responsibilities:
- `noretval()` emits synthetic use markers for integer and floating return values to prevent incorrect unused-return assumptions.
- `commute()` reorders commutative operands by complexity.
- `indexshift()` detects shift-left patterns usable as x86 scaled indexes.
- `xcom()` is the main complexity/addressability pass, classifying constants, names, registers, addresses, indirections, indexed addressing, arithmetic, shifts, multiply/divide/modulo simplifications, comparisons, calls, and 64-bit operations.
- Rewrites power-of-two multiply/divide/modulo into shifts or masks where valid.
- Folds address constants into base expressions.
- Builds `OINDEX` nodes for x86 base/index/scale addressing.
- `indx()` chooses base and index trees and records them in global `idx`.

Integration points:
- Runs before `cgen()` to guide register allocation and addressing choices.
- Depends on shared compiler helpers like `vlog()`, `side()`, `simplifyshift()`, `rolor()`, `com64()`, and type tables.
- `txt.c` later consumes `idx` through `doindex()`/`naddr()`.

Risks and invariants:
- `addable` numeric classes are local compiler conventions; many later code paths assume their exact meanings.
- Some transformations mutate tree structure and type fields.
- Indexed addressing is skipped for expressions with side effects.
