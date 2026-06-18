# sources/storage-engines/sqlite/ext/misc/explain.c

## Purpose

`explain.c` implements an eponymous virtual table `explain` that turns `EXPLAIN <sql>` bytecode output into queryable rows. It was written to simplify tests that assert bytecode patterns.

## Important APIs, types, and functions

`sqlite3_explain_init()` calls `sqlite3ExplainVtabInit()`, registering module `explain`. `explain_vtab` stores the connection. `explain_cursor` stores the original SQL text, prepared `EXPLAIN` statement, and last step result. The declared schema is `addr, opcode, p1, p2, p3, p4, p5, comment, sql HIDDEN`.

## Control flow

`explainBestIndex()` requires a usable equality constraint on hidden column `sql`; if only unusable SQL constraints exist it returns `SQLITE_CONSTRAINT`, and if no usable constraint exists the plan remains expensive/unusable. `explainFilter()` copies the SQL text, prefixes it with `EXPLAIN `, prepares it on the same connection, and steps to the first row. `explainNext()` steps the prepared statement. `explainColumn()` returns the hidden SQL text for the hidden column and otherwise forwards the corresponding `sqlite3_column_value()` from the EXPLAIN statement. `explainRowid()` uses the bytecode address column.

## State and persistence

The module is read-only. Each cursor owns one prepared EXPLAIN statement and copied SQL string. No persistent database state is changed, though preparing SQL can resolve schema metadata and fail if referenced objects are invalid.

## Dependencies and integration points

It depends on virtual table APIs and SQLite's EXPLAIN output column layout. It is used as a table-valued helper for tests and introspection, for example filtering rows by opcode.

## Risks

The module assumes EXPLAIN output columns match the declared schema. SQL text is concatenated after `EXPLAIN`, so caller input must be a single statement acceptable to SQLite prepare. Non-text `sql` arguments produce empty output. Errors from prepare or step propagate as virtual table errors. The module is not marked direct-only or innocuous in this file, so embedding context depends on SQLite's module policy at registration.

## Test signals

Tests should query `explain('SELECT ...')`, filter by opcode, verify hidden SQL column echo, rowid equals address, non-text SQL returns EOF, missing SQL constraint is rejected by planning, invalid SQL propagates an error, and bytecode output remains aligned with SQLite EXPLAIN schema.
