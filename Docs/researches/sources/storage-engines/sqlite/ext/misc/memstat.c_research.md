# sources/storage-engines/sqlite/ext/misc/memstat.c

Purpose: implements `sqlite_memstat`, an eponymous virtual table that reports SQLite global and per-connection memory/cache counters.

Important APIs/types/functions: `memstat_vtab` stores the `sqlite3 *`; `memstat_cursor` stores row/schema position and current/highwater values. `aMemstatColumn[]` defines metrics. Key methods are `memstatConnect()`, `memstatFindSchemas()`, `memstatNext()`, `memstatColumn()`, and `sqlite3MemstatVtabInit()`.

Control flow: `xFilter` snapshots `PRAGMA database_list`. `xNext` iterates each metric and schema where applicable, calling `sqlite3_status64()`/`sqlite3_status()`, `sqlite3_db_status()`, or optional ZIPVFS file-controls, skipping unavailable ZIPVFS rows.

State and persistence: only transient cursor-owned schema-name copies and live metric values. No writes.

Dependencies/integration: SQLite virtual tables and status APIs, with compile-time gating for core builds, omitted vtabs, SQLite version counters, and ZIPVFS.

Risks/test signals: version-dependent counters, schema allocation cleanup, nullability masks, and ZIPVFS skip behavior. Test querying all rows, attached databases, omitted-vtab builds, metric highwater values, and read-only operation.
