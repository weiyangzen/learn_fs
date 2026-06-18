# File Research: sources/os/plan9/9front/sys/src/cmd/cc/funct.c

Implements the Plan 9 C compiler’s `typestr` operator/function rewriting extension.

Key behavior:
- `isfunct` recognizes operators on special struct/union types with `Type.funct` metadata and rewrites them into `OFUNC` calls.
- Supports binary arithmetic/bitwise operators, comparisons, compound assignments, unary operators, and casts to/from scalar types.
- For compound assignments, inserts an address-of left operand so helper functions receive `T*`.
- Validates helper function type compatibility with `tcompat` and argument compatibility with `tcoma`.
- `dclfunct` synthesizes external helper declarations from a generated structure tag naming convention.
- Helper names are generated from `ftabinit` and `gtabinit`, such as `<tag>_add_`, `<tag>_eq_`, `<tag>_asadd_`, and scalar conversion helpers.

Dependencies:
- Uses compiler core types and AST helpers from `cc.h`: `Node`, `Type`, `Sym`, `Funct`, `new`, `typ`, `copytyp`, `dodecl`, `tcomo`, `tcompat`, and `tcoma`.

Research notes:
- This is not ordinary C operator overloading; it is a Plan 9 compiler extension tied to `typestr`.
- Rewrites preserve diagnostics by setting bad nodes to type `T` after reporting failed conversions.
