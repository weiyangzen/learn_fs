# File Research: sources/os/plan9/9front/sys/src/cmd/5c/machcap.c

This file decides whether the ARM backend can directly handle selected AST operations, especially for 64-bit lowering.

Behavior:
- `machcap(Node *n)` returns true for:
  - integer/vlong add/sub/and/xor/or and their assignment forms when operands and result are vlong-compatible,
  - `OMUL`/`OLMUL` when result is vlong and operands are integer/long with matching signedness,
  - constant shifts and shift-assigns over vlong-compatible operands,
  - casts between integer/pointer-like types and vlong-compatible types.
- Returns false for unsupported nodes or null test calls.

Dependencies and interactions:
- Used by `cgen64()` in `cgen.c` to decide whether to handle 64-bit operations inline.
- Relies on common type-class arrays such as `typev`, `typeil`, `typeu`, and `typeilp`.

Research relevance:
- Small file but important gatekeeper for 64-bit code generation.

Risk notes:
- If it returns true too broadly, `cgen64()` may see unsupported shapes.
- If it returns false too often, operations fall back to slower or unsupported generic paths.
