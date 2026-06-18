# sources/storage-engines/sqlite/ext/misc/diskused.c

## Purpose

`diskused.c` implements SQL function `diskused(X)`, a textual database storage-utilization report for schema `X`. It replaces the old `sqlite3_analyzer` utility path and is used by the SQLite CLI `.diskused` command.

## Important APIs, types, and functions

`sqlite3_diskused_init()` registers `diskused` as an innocuous one-argument function. `DiskUsed` stores the database handle, SQL function context, output `sqlite3_str`, randomized temp table name, and target schema. `diskusedSql()`, `diskusedSqlInt()`, `diskusedPrepare()`, and `diskusedStmtFinish()` centralize dynamic SQL execution and error reporting. `diskusedTitle()`, `diskusedLine()`, and `diskusedPercent()` format the report. `diskusedSubreport()` aggregates page and payload statistics for selected subsets of objects.

## Control flow

`diskusedFunc()` resolves NULL schema to `main`, rejects `temp`, validates the schema through `pragma_database_list`, creates a random `temp.diskused...` table, then populates it from `dbstat(schema)` joined to schema-derived table/index metadata. It reads `page_count`, `page_size`, `freelist_count`, `auto_vacuum`, table counts, WITHOUT ROWID counts, and index counts. It emits high-level storage totals, page-count rankings, aggregate subreports for all tables/indexes and categories, per-table and per-index subreports, and finally SQL that can recreate the raw `space_used` data used by the report.

## State and persistence

The function creates a temporary table with a 128-bit random suffix and drops it in `diskusedReset()`. Output accumulates in memory until returned as a single text result. It does not modify the target schema, but it requires `dbstat` visibility over that schema.

## Dependencies and integration points

It depends on SQLite `dbstat`, schema tables, pragma table-valued functions, `pragma_table_list`, `pragma_index_list`, `sqlite3_randomness()`, dynamic SQL quoting with `%w` and `%Q`, and math `ceil()` for auto-vacuum overhead. It is closely tied to SQLite page accounting semantics.

## Risks

The function is innocuous but can be expensive on large databases because it scans `dbstat` and builds a full report string. Temporary table cleanup must run on every error path; many helpers call `diskusedReset()` after reporting errors. Division by storage totals assumes nonzero page counts and object storage in subreports. If `dbstat` is unavailable or shadowed, analysis fails. Report text is not machine-stable enough for strict string tests across SQLite storage changes.

## Test signals

Tests should include empty databases, invalid schema names, rejected `temp`, rowid and WITHOUT ROWID tables, indexes and autoindexes, freelist pages, auto-vacuum databases, overflow payloads, attached schemas, `dbstat` unavailable/error cases, temp table cleanup after errors, and presence of the raw `space_used` SQL block.
