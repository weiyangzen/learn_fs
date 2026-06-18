# File Research: sources/os/plan9/9front/sys/src/cmd/5c/sgen.c

This file computes ARM backend expression addressability and complexity, and emits no-return-value markers.

Key routines:
- `noretval(int n)` emits `ANOP` markers referencing integer and/or floating return registers so the optimizer treats return values as used or unavailable.
- `xcom(Node *n)` computes `n->addable` and `n->complex` recursively.
- Recognizes directly addressable constants, registers, indirect registers, names, address-of names/indirects, dereferences, and constant-offset additions.
- Rewrites some operations:
  - multiply or multiply-assign by powers of two becomes shift or shift-assign,
  - unsigned divide/mod by powers of two becomes logical shift or mask,
  - OR expressions may be transformed by `rolor()` for integer-like types,
  - 32-to-64 cast patterns in multiplies can be lifted so `cgen64()` can use 32x32 multiply instructions.
- Computes complexity as a register-pressure estimate, marking function calls as `FNX`.
- Moves constants to the right side for immediate-friendly operations.

Dependencies and interactions:
- Called by common compiler analysis before code generation.
- Feeds `cgen.c` decisions about direct addressing, temporary allocation, and operation selection.

Research relevance:
- This is the expression-shape normalization layer for the ARM backend.

Risk notes:
- It mutates AST nodes in place, including opcode and child swaps.
- Correct complexity estimates are important for preserving evaluation order around side effects and function calls.
