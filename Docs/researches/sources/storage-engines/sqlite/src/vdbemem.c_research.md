# sources/storage-engines/sqlite/src/vdbemem.c research

## Purpose
`vdbemem.c` implements the VDBE `Mem`/`sqlite3_value` runtime value container. It owns conversions between SQLite manifest types, text encodings, dynamic/static/ephemeral ownership modes, aggregate accumulator finalization, rowset and pointer bindings, btree payload extraction, constant-expression value materialization, and STAT4 probe-value construction.

## Important APIs, types, and functions
Key APIs include `sqlite3VdbeMemGrow()`, `sqlite3VdbeMemClearAndResize()`, `sqlite3VdbeMemMakeWriteable()`, `sqlite3VdbeMemExpandBlob()`, `sqlite3VdbeMemStringify()`, numeric conversion helpers, cast/affinity helpers, set/release/copy helpers, `sqlite3ValueText()`, `sqlite3ValueBytes()`, `sqlite3VdbeMemFromBtree()`, and STAT4 helpers. Debug builds validate `Mem` ownership and dual-representation invariants through `sqlite3VdbeCheckMemInvariants()` and `sqlite3VdbeMemValidStrRep()`.

## Control flow
Value replacement clears destructible content, installs a new scalar/string/blob/pointer/rowset representation, and updates flags. String/blob assignment branches on `xDel`: transient data is copied, dynamic data is adopted, and static/ephemeral data is referenced. Numeric conversion either preserves dual representations or forces a target type for casts. Btree extraction tries an ephemeral local-page pointer before allocating. STAT4 expression extraction handles literals, casts, unary minus, true/false, blob literals, bound variables on reprepare, and selected constant functions.

## State and persistence behavior
State is in-memory per `Mem`, but a `Mem` may point into btree pages, bound values, aggregate contexts, rowsets, or owned allocations. Ownership is controlled by `z`, `zMalloc`, `szMalloc`, `xDel`, and flags. The file does not persist schema data, but STAT4 helpers create planner probe records.

## Dependencies and integration points
Depends on VDBE internals, btree payload APIs, SQLite allocation, UTF conversion, numeric parsers, expression/function metadata, `RowSet`, `FuncDef`, `Index`, and `UnpackedRecord`. It is used by opcodes, SQL functions, binding/result APIs, record comparison, query planning, and tracing.

## Risks and test signals
Major risks are incorrect ownership flags, double-free/leak behavior, UTF16 termination, lazy zeroblob expansion, inconsistent state after failed btree reads, and subtle numeric affinity semantics. Test with all ownership modes, UTF encodings, zeroblobs, pointers, rowsets, aggregate/window finalization, casts, size limits, corrupt records, STAT4 probes, OOM fault injection, and debug invariant builds.
