# sources/storage-engines/sqlite/src/vdbetrace.c research

## Purpose
`vdbetrace.c` expands host parameters into SQL text for trace/debug output. It renders current VDBE bindings as SQL literals and comments recursive VDBE SQL text.

## Important APIs, types, and functions
`findNextHostParameter()` tokenizes SQL with `sqlite3GetToken()` to find `TK_VARIABLE` tokens outside quoted text and comments. `sqlite3VdbeExpandSql()` scans raw SQL, resolves positional/named parameters, renders `Mem` values, and returns an allocated string.

## Control flow
If `db->nVdbeExec > 1`, every line is prefixed with `-- `. If the statement has no variables, raw SQL is copied. Otherwise the function appends text before each parameter, maps `?`, `?NNN`, `:name`, `$name`, `@name`, or `#name` to a bind index, and renders NULL, integer, real, text, zeroblob, or blob values. UTF16 text is converted through a temporary UTF8 `Mem`.

## State and persistence behavior
The file has no persistent state. It reads `p->aVar`, may allocate temporary conversion memory, and returns one transient trace string owned by the caller.

## Dependencies and integration points
Compiled only when tracing is enabled. Depends on tokenization, VDBE parameter lookup, `Mem` flags and conversion, `StrAccum`, SQLite printf quoting, and optional `SQLITE_TRACE_SIZE_LIMIT`.

## Risks and test signals
Trace output may expose sensitive bound values and can be very large without a size limit. Tests should cover all parameter syntaxes, repeated named parameters, recursive execution, all value types, quote/blob rendering, UTF16 conversion, truncation at UTF8 boundaries, and OOM accumulator paths.
