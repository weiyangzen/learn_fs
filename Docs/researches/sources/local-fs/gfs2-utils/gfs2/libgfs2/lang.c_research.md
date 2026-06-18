# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/lang.c

This file implements AST creation, AST interpretation, block lookup, field printing, and metadata assignment for the GFS2 language.

Public APIs:
- `ast_new()`, `ast_destroy()`
- `lgfs2_lang_result_next()`
- `lgfs2_lang_result_print()`
- `lgfs2_lang_result_free()`

Main behavior:
- Converts lexer tokens into AST nodes with numeric/string/path values.
- Resolves block references by absolute address, named IDs (`sb`, `master`, `root`, `rindex`), paths, resource group subscript (`rgrp[n]`), and offsets.
- `get` reads a block, detects metadata type, and prints all known fields.
- `get ... state` returns allocation bitmap state.
- `set` reads a block, optionally writes a metadata header for an explicit type, assigns listed fields, and writes the block back.
- Field printing handles UUIDs, strings, and 1/2/4/8-byte big-endian numeric values.
- Field assignment handles UUID parsing, bounded strings, and big-endian numeric storage.

Integration role:
- Consumes metadata descriptions from `meta.c`.
- Uses libgfs2 inode lookup, block reads, bitmap access, resource group reads, and field assignment helpers.
- Used by `gfs2l.c`.

State and ownership:
- Results own `lr_buf` and are released by `lgfs2_lang_result_free()`.
- AST nodes own duplicated text/string buffers.
- Path lookup mutates the stored path string through `strtok_r()` and unescaping.

Risk notes:
- Path lookup destructively tokenizes `ast_str`, so reusing the same AST path can behave differently.
- `set` writes metadata directly and has no transaction/recovery wrapper.
- Numeric parsing uses `sscanf(... SCNi64)` into a `uint64_t` field through a mismatched signed format expectation.
- Result iteration stops on the first failing statement and does not continue.
