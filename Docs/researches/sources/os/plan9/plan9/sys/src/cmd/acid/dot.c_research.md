# File Research: sources/os/plan9/plan9/sys/src/cmd/acid/dot.c

Acid complex type definition and field-selection support.

Key responsibilities:
- Searches type member lists by name.
- Evaluates dot/arrow-style field access by adding offsets and applying member format/type metadata.
- Builds nested `Type` structures from parsed complex declarations.
- Defines complex types in the symbol table.
- Handles declarations binding names to type metadata.

Dependencies:
- Uses `Type`, `Node`, `Lsym`, `gmalloc`, `look`, `mkvar`, and expression evaluation helpers.

Notable risks:
- Type layout is script-defined and must match target ABI/debugger expectations.
- Field offsets/formats are stored in parsed nodes and transferred into custom type structures.
