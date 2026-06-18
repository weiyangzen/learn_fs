# sources/storage-engines/sqlite/src/delete.c

## Purpose

`delete.c` generates VDBE bytecode for `DELETE FROM` statements and provides shared helpers used by DELETE, UPDATE, INSERT, triggers, foreign keys, and index maintenance. It handles table lookup, read-only policy, view materialization, optional `ORDER BY/LIMIT` rewriting, truncate optimization, one-pass deletion, virtual tables, row triggers, foreign keys, change counts, and index-entry deletion.

## Important APIs, Types, and Functions

- `sqlite3SrcListLookup()` resolves a single-table `SrcList` and handles `INDEXED BY`.
- `sqlite3CodeChangeCount()` emits row-change result code after `OP_FkCheck`.
- `vtabIsReadOnly()`, `tabIsReadOnly()`, and `sqlite3IsReadOnly()` enforce virtual table, view, system table, shadow table, trusted-schema, and writable-schema restrictions.
- `sqlite3MaterializeView()` evaluates a view into an ephemeral table for INSTEAD OF trigger processing.
- `sqlite3LimitWhere()` rewrites `DELETE/UPDATE ... WHERE ... ORDER BY ... LIMIT ...` into a `rowid IN (SELECT ...)` or primary-key vector `IN` expression.
- `sqlite3DeleteFrom()` is the main code generator for DELETE statements.
- `sqlite3GenerateRowDelete()` emits bytecode to delete one row, including OLD registers, BEFORE/AFTER triggers, foreign-key checks/actions, index deletion, and table deletion.
- `sqlite3GenerateRowIndexDelete()` emits `OP_IdxDelete` for all relevant indexes.
- `sqlite3GenerateIndexKey()` builds index key registers and optionally records partial-index skip labels.
- `sqlite3ResolvePartIdxLabel()` resolves partial-index skip labels.

## Control Flow and Behavior

`sqlite3DeleteFrom()` first resolves the target table, finds triggers, determines whether foreign keys make the statement complex, applies the optional update/delete-limit rewrite, initializes views, checks read-only and authorizer rules, assigns cursors, opens a write operation, materializes views if needed, resolves WHERE expressions, and optionally initializes a row-change counter.

If the statement is a simple full-table delete, the authorizer did not return `SQLITE_IGNORE`, there are no triggers/FKs, the table is not virtual, and preupdate hooks are absent, it emits `OP_Clear` for the table and indexes. Otherwise it builds a WHERE loop to collect rowids or primary keys. Rowid tables use a RowSet for two-pass deletes; WITHOUT ROWID tables use an ephemeral table containing primary-key records. If the query planner supports one-pass deletion, the row key is kept in registers and cursors already positioned by the WHERE loop are reused.

The actual row deletion path handles virtual tables with `OP_VUpdate` and ordinary tables through `sqlite3GenerateRowDelete()`. For ordinary tables, row deletion seeks the row if not already positioned, populates OLD.* registers when triggers or FKs require them, fires BEFORE triggers, re-seeks if triggers may have moved/deleted the row, performs FK checks, deletes secondary index entries, emits `OP_Delete` for the canonical table or primary-key cursor, runs FK actions, and fires AFTER triggers.

`sqlite3GenerateRowIndexDelete()` skips the primary-key index for WITHOUT ROWID tables and can skip a cursor already positioned by one-pass planning. It uses `sqlite3GenerateIndexKey()` to load index columns, evaluate partial-index predicates, reuse registers from the prior index when safe, and generate record keys as needed.

## State and Persistence

The file emits VDBE programs rather than executing deletions immediately. Runtime persistence is through VDBE opcodes that mutate table and index B-trees, virtual tables, autoincrement metadata, foreign-key side effects, and change counters. During code generation it mutates parser state such as cursor numbers, memory register allocation, trigger context, `isMultiWrite`, authorization context, and temporary expression trees. Cleanup always deletes source lists and expressions.

## Dependencies and Integration Points

This code is tightly integrated with the parser, name resolver, WHERE planner, VDBE emitter, B-tree cursor opening, authorization, trigger subsystem, foreign-key subsystem, virtual table subsystem, view expansion, autoincrement handling, update/delete-limit extension, preupdate/update hooks, and schema policy flags. It also shares helpers with UPDATE and integrity-check/index code paths.

## Risks and Edge Cases

DELETE semantics are highly conditional. The truncate optimization must be disabled for authorizer `SQLITE_IGNORE`, triggers, FKs, virtual tables, and preupdate hooks so hooks and constraints observe row-level behavior. BEFORE triggers can move cursors or delete the row, requiring a re-seek and disabling no-seek index optimization. WITHOUT ROWID primary-key vectors must match SELECT outputs in `sqlite3LimitWhere()`. Partial-index predicates can clobber reused registers, so prior-key caching is disabled after evaluating them. Virtual table direct-only/trusted-schema risk checks must reject unsafe trigger or DDL usage. Cleanup must avoid leaking duplicated WHERE/ORDER/LIMIT trees across rewrite paths.

## Test Signals

Tests should include simple rowid deletes, WITHOUT ROWID deletes, full-table truncate optimization and cases that disable it, `ORDER BY/LIMIT/OFFSET` deletes, composite primary-key `IN` rewrites, views with INSTEAD OF triggers, BEFORE triggers that delete or move rows, AFTER triggers, cascading and restricting foreign keys, virtual table deletes and read-only virtual tables, direct-only and innocuous virtual table policy under trusted-schema settings, system/shadow table restrictions, authorizer `SQLITE_DENY` and `SQLITE_IGNORE`, count-changes behavior, preupdate/update hooks, partial indexes, expression indexes, one-pass single and multi-row plans, and OOM cleanup paths.
