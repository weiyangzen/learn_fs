# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/print.c

This file implements pretty-printing and introspection output for the Acid debugger language. It prints function definitions, symbol/type metadata, expression trees, statement trees, and string literals.

Key behavior:
- `fundefs()` scans the Acid symbol hash, collects built-in and user-defined procedures, sorts names, and prints them in columns.
- `whatis()` reports variable types/formats, complex type layouts, procedure definitions, builtins, or undefined symbols.
- `pcode()` and `pexpr()` recursively print Acid AST nodes, covering control flow, local declarations, complex declarations, calls, indexing, casts, formatting, assignments, unary/binary operators, list constructs, and `whatis`.
- `pstr()` emits escaped string literals.

Important details:
- Output is routed through global `bout` using Plan 9 `Biobuf`.
- The printer depends on `acid.h` node op codes, type tags, symbol layout, and global hash table.
- Binary operator spellings are table-driven by Acid op enum values.
- Formatting is mostly diagnostic/source-like, not a general parser round-trip guarantee.

Filesystem relevance:
- Indirect: supports debugger interaction with symbols and values, not filesystem code itself.
