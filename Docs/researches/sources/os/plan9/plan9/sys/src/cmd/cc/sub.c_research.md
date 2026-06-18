# File Research: sources/os/plan9/plan9/sys/src/cmd/cc/sub.c

This file is a large shared utility module for compiler AST/type construction, type compatibility, expression rewriting, diagnostics, and static initialization tables.

Key behavior:
- Allocates and prints AST nodes with `new()`, `new1()`, `prtree()`, and `prtree1()`.
- Builds/copies/qualifies types and maps parser type/class bitmasks to compiler type/class objects.
- Checks type compatibility, assignment/cast compatibility, no-op casts, nil casts, and usual arithmetic conversions.
- Supports structure field lookup, unnamed substructure lookup, field-offset materialization, and bitfield access rewriting.
- Rewrites pointer arithmetic and pointer subtraction with element-size scaling.
- Simplifies shift/mask patterns in `simplifyshift()`.
- Detects side effects, constant small values, power-of-two constants, relation inversion/indexing, and list reversal.
- Emits diagnostics, warnings, yacc errors, and fatal errors with source-location formatting.
- Initializes name tables, type-class tables, operation names, relation maps, type compatibility masks, and hash constants in `tinit()`.
- Determines whether statement trees have “dead heads” for reachability analysis.

Important details:
- `typeext()` implements Plan 9 C extensions for unnamed embedded struct/union assignment and pointer conversion.
- `constas()` warns about discarding const qualifiers through assignment.
- `relcon()` narrows constants to avoid widening variables in comparisons.
- Most compatibility logic is table-driven through initialized masks such as `tadd`, `tsub`, `tcast`, `trel`, and `tasign`.

Filesystem relevance:
- Indirect compiler support; no direct filesystem behavior.
