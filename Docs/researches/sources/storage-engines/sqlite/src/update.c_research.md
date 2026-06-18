# sources/storage-engines/sqlite/src/update.c

## Purpose
`update.c` is SQLite's UPDATE statement code generator. It lowers parsed `UPDATE`, `UPDATE FROM`, limited UPDATE, view-update, virtual-table update, trigger, foreign-key, generated-column, RETURNING-compatible, and UPSERT `DO UPDATE` paths into VDBE bytecode. The file is not a storage engine by itself, but it is one of the central write-path bridges between SQL syntax and persistent table/index btrees.

## Important APIs, Types, And Functions
The exported entry points are `sqlite3Update()` and `sqlite3ColumnDefault()`. `sqlite3Update()` owns normal table UPDATE code generation and is also reused by `upsert.c` for `ON CONFLICT DO UPDATE`. `sqlite3ColumnDefault()` annotates `OP_Column` reads with ALTER TABLE default values and adds `OP_RealAffinity` for REAL columns stored as integers.

Private helpers include `indexColumnIsBeingUpdated()` and `indexWhereClauseMightChange()` for deciding which indexes must be opened and rewritten; `exprRowColumn()` for synthetic `TK_ROW` references used by `UPDATE FROM`; `updateFromSelect()` for staging key plus SET-expression results into an ephemeral table; and `updateVirtualTable()` for the separate virtual-table `OP_VUpdate` path. Key data structures are `Parse`, `SrcList`, `Table`, `Index`, `ExprList`, `Expr`, `WhereInfo`, `Vdbe`, `NameContext`, `AuthContext`, `Trigger`, and `Upsert`.

## Control Flow
`sqlite3Update()` first resolves the target table, triggers, view status, read-only status, cursor allocation, and the `aXRef[]` mapping from table columns to SET-list expressions. It identifies rowid/IPK and WITHOUT ROWID primary-key changes, rejects writes to generated columns, applies the authorizer, propagates generated-column dependencies through `aXRef[]`, and computes whether foreign-key work or REPLACE conflict handling may be needed.

For `UPDATE FROM`, it calls `updateFromSelect()` to build a SELECT that emits target keys plus SET values into an ephemeral table. For ordinary rowid tables without `UPDATE FROM`, it may collect rowids in a RowSet/ephemeral table before mutation. For WITHOUT ROWID tables, views, or `UPDATE FROM`, it stages composite primary-key records or view rows. For eligible ordinary updates it asks `where.c` for a one-pass plan and disables one-pass multi-row updates if the selected scan index is being modified.

The mutation loop loads old row content when triggers, primary-key changes, or foreign keys need it; computes new row registers; computes generated columns; fires BEFORE triggers; reloads unmodified columns after BEFORE triggers; runs constraint checks; reseeks if conflict handling moved the cursor; performs FK checks; deletes old index entries and possibly the old table row; inserts the new row and index entries; runs FK actions; increments row counts; fires AFTER triggers; and advances either the WHERE cursor or the staged ephemeral table.

Virtual tables bypass the btree rewrite path. `updateVirtualTable()` gathers old rowid, new rowid, and every column value into registers or an ephemeral table, preserves unchanged-column markers with `OPFLAG_NOCHNG`, uses a one-pass strategy only when the virtual table guarantees at most one row, and emits `OP_VUpdate` with the selected conflict policy.

## State And Persistence Behavior
This file persists changes only through generated VDBE opcodes. Persistent effects include table row replacement, index entry deletion/insertion, sqlite_sequence finalization for top-level updates, FK cascading actions, trigger side effects, virtual-table `xUpdate` calls, and VACUUM-independent btree writes coordinated by `sqlite3BeginWriteOperation()` and `sqlite3MultiWrite()`. Intermediate state is held in VDBE registers, RowSets, ephemeral tables, cursor arrays, `aXRef[]`, `aRegIdx[]`, `aToOpen[]`, trigger masks, and `WhereInfo`.

Correctness depends on conservative index maintenance. A false positive in `indexColumnIsBeingUpdated()` or `indexWhereClauseMightChange()` only opens or rewrites extra indexes; a false negative can leave persistent indexes corrupt. Generated columns are treated as updated when their expressions depend on updated columns so constraints and indexes see recomputed values. ALTER TABLE-added defaults are attached to column reads so older records missing appended columns still return the declared default.

## Dependencies And Integration Points
`update.c` depends on name resolution (`resolve.c`), expression code generation (`expr.c`), WHERE planning (`where.c`), SELECT code generation (`select.c`) for `UPDATE FROM`, insert/index helpers (`insert.c`), triggers (`trigger.c`), foreign keys (`fkey.c`), generated columns (`build.c`/expression helpers), authorization (`auth.c`), virtual tables (`vtab.c`), rowsets (`rowset.c`), and UPSERT (`upsert.c`). The VDBE opcodes it emits integrate with `vdbe.c`, btree cursors, preupdate/update hooks, and the RETURNING/count-changes machinery.

## Risks And Edge Cases
High-risk areas are one-pass eligibility, index-change detection, BEFORE-trigger reload semantics, REPLACE conflict handling, primary-key rewrites on WITHOUT ROWID tables, `UPDATE FROM` staging order, and virtual-table no-change markers. Mutating a scan index in one-pass multi-row mode can loop or skip rows, so the fallback check is critical. BEFORE triggers can delete or modify the row being updated; this file intentionally skips later work if the row vanished and reloads only unmodified columns if it survived. `UPDATE FROM` must keep SET-expression columns aligned after key columns in the ephemeral table. UPSERT reuse requires cursors already opened by INSERT and skips normal row discovery.

## Test Signals
Relevant SQLite tests include `update.test`, `update2.test`, `update3.test`, `update4.test`, `updatevtab.test`, `wherelimit.test`, `hook.test`, `trigger*.test`, `fkey*.test`, generated-column tests, `upsert*.test`, and `returning*.test`. Strong regressions are EXPLAIN changes around one-pass UPDATE, failures of `PRAGMA integrity_check` after indexed updates, incorrect row counts, preupdate-hook column mismatches, generated-column update errors, virtual-table `sqlite3_vtab_nochange()` behavior, `UPDATE FROM` result mismatches, and FK cascade differences.
