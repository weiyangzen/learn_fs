# sources/storage-engines/sqlite/src/vdbevtab.c research

## Purpose
`vdbevtab.c` implements diagnostic virtual tables/table-valued functions for inspecting prepared statement bytecode: `bytecode` and `tables_used`.

## Important APIs, types, and functions
`bytecodevtab` stores the database and mode. `bytecodevtab_cursor` stores the target statement, row/address, subprogram state, current opcode pointer, cached P4/comment strings, table metadata cache, and a `Mem` used by subprogram traversal. The module callbacks implement connect, open/close, best-index, filter, next, eof, column, and rowid. `sqlite3VdbeBytecodeVtabInit()` registers both modules.

## Control flow
`bytecode` declares opcode columns plus hidden `stmt`; `tables_used` declares type/schema/name/write/subprogram plus hidden `stmt`. `xBestIndex` requires `stmt = ?` and can use `subprog IS NULL` to omit subprograms. `xFilter` accepts SQL text or a `"stmt-pointer"`, prepares/finalizes owned SQL text statements, and positions with `sqlite3VdbeNextOpcode()`. `xColumn` renders opcode fields, P4, comments, subprogram labels, scan counters, and table/index names from root-page operands.

## State and persistence behavior
Read-only diagnostic state lives in the cursor. It owns optional prepared statements and cached allocations and reads live VDBE opcode arrays. It does not change the target statement or schema.

## Dependencies and integration points
Depends on the virtual table subsystem, VDBE opcode display helpers, schema hashes, pointer-valued SQL arguments, optional explain comments, and optional statement scanstatus. It is registered per connection when `SQLITE_ENABLE_BYTECODE_VTAB` is enabled.

## Risks and test signals
Risks include invalid statement pointers, mandatory hidden-argument planning, stale schema/root-page mapping, P4 allocation cleanup, and build-option-dependent columns. Test SQL and pointer inputs, subprograms from triggers/FKs, `tables_used` read/write detection, invalid stmt values, repeated cursor reuse, explain comments, and scanstatus on/off.
