# File Research: sources/os/plan9/9front/sys/src/cmd/7l/mod.c

Import/export symbol-table support for dynamically loadable modules.

Key functions:
- `readundefs` reads whitespace-separated symbol names from a file and marks them as import/export references.
- `undefsym` assigns an import index to an unresolved external symbol and converts it to `SUNDEF`.
- `zerosig` clears a symbol signature.
- `import` walks the symbol hash table and converts matching signed external references into imports.
- `ckoff` validates relocation offsets against the relocation address bit budget.
- `newdata` creates synthetic `ADATA` records.
- `export` builds the `_exporttab` data object and associated `.string` storage for exported symbols.

Important details:
- Exported symbols are collected from signed, defined symbols and sorted by name.
- Each export table entry contains signature, address, and name pointer.
- The table ends with three zero words.
- `export` synthesizes data records rather than writing bytes directly, so normal data layout/output handles the result.

Filesystem relevance: indirect. This supports Plan 9 module linking, not filesystem code.
