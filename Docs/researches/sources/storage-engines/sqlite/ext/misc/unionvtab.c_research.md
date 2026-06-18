# sources/storage-engines/sqlite/ext/misc/unionvtab.c

## Purpose
Implements read-only `unionvtab` and `swarmvtab` virtual tables that expose multiple rowid tables with compatible schemas and non-overlapping rowid ranges as one virtual table.

## Important APIs, Types, And Functions
Key structs are `UnionSrc`, `UnionTab`, and `UnionCsr`. Important functions include `unionConnect`, `unionSourceCheck`, `unionSourceToStr`, `unionOpenDatabase`, `unionOpenDatabaseInner`, `unionConfigureVtab`, `unionFilter`, `unionNext`, `doUnionNext`, `unionBestIndex`, `unionFinalizeCsrStmt`, `unionIncrRefcount`, and `createUnionVtab`.

## Control Flow
`unionConnect()` requires TEMP schema, prepares the source SQL sorted by minimum rowid, builds `aSrc`, rejects empty sources and overlapping ranges, validates schemas, declares a virtual schema from the first source, and records the integer primary key column if present. `unionvtab` sources must already be in the main connection or attached databases. `swarmvtab` treats the first source column as a filename/URI, opens source databases lazily, optionally invokes `missing` and `openclose` UDFs, and enforces a maximum open-source cache. `xBestIndex` consumes rowid or integer-primary-key equality/range constraints. `xFilter` builds a UNION ALL query for `unionvtab` or scans one swarm source at a time.

## State And Persistence Behavior
The virtual tables are read-only. Runtime state includes source metadata, optional callback statements, open swarm database handles, a closable LRU-like list, per-source user counts, and cursor statements. No source data is modified.

## Dependencies And Integration Points
Depends on SQLite virtual table APIs, `pragma_table_info`, `sqlite3_table_column_metadata`, `sqlite3_open_v2()` with `SQLITE_OPEN_READONLY|SQLITE_OPEN_URI`, prepared statements, and application UDFs for swarm file materialization and open/close notification.

## Risks And Edge Cases
Correctness depends on truthful, non-overlapping rowid bounds from the configuration query. `unionvtab` validates all source schemas at connect time, while `swarmvtab` validates each database as opened and compares to the first schema string. Dynamic SQL quotes identifiers, but source SQL and callback names remain user-provided configuration. `maxopen` is best effort because active cursors pin sources. The read-only module does not prevent underlying source tables from changing row ranges after connection.

## Test Signals
Tests should cover TEMP-only enforcement, wrong argument counts, empty source SQL, overlapping ranges, schema mismatch, rowid and integer-primary-key constraints, range boundary off-by-one cases, read-only update rejection, swarm missing/openclose callbacks, maxopen closure behavior, context columns, SQL parameter binding options, and concurrent cursors.
