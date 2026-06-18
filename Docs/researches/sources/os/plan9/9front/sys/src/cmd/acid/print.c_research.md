# File Research: sources/os/plan9/9front/sys/src/cmd/acid/print.c

This file implements Acid's source-level pretty-printing and symbol-description output.

Key responsibilities:
- Maintains printable names for binary operators and Acid value type names.
- `fundefs()` collects all user-defined and builtin function names from the global hash table, sorts them, and prints them in columns.
- `whatis()` reports what a symbol is: variable with type/format, complex type definition, function definition, builtin function, or undefined.
- `pcode()` and `pexpr()` recursively render Acid AST nodes back into readable source-like text.
- `pstr()` prints Acid strings with C-style escapes for control characters, backslash, and quote.

Important dependencies:
- Uses global Acid state from `acid.h`: `hash`, `bout`, `Node`, `Lsym`, `Type`, `String`.
- Uses Plan 9 `Biobuf` output APIs (`Bprint`, `Bputc`).
- AST opcodes map directly to parser/evaluator node kinds.

Filesystem/storage relevance:
- No direct filesystem operations. This is diagnostic and introspection support for the Acid debugger, useful for understanding runtime command definitions and type metadata.

Notes:
- Pretty-printing is conservative and parenthesizes most binary expressions.
- Indentation uses a fixed tab string and precision formatting, so very deep nesting is bounded by the static tab buffer.
