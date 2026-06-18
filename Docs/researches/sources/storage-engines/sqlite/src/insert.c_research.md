# sources/storage-engines/sqlite/src/insert.c

## Purpose

`insert.c` is SQLite's parser-side code generator for `INSERT` statements and the shared write helpers used by `UPDATE` paths. It does not execute inserts directly. Instead, it emits VDBE bytecode for resolving input rows, applying defaults and affinities, computing generated columns, checking constraints, running triggers, writing table/index b-trees, maintaining `sqlite_sequence`, and optionally applying the raw transfer optimization for `INSERT INTO dst SELECT * FROM src`.

The file covers ordinary rowid tables, `WITHOUT ROWID` tables, views with triggers, virtual tables, strict tables, generated columns, UPSERT, foreign keys, recursive trigger side effects, preupdate hooks, `RETURNING` support hooks, and VACUUM-oriented bulk-copy paths.

## Important APIs, Types, And Functions

- `sqlite3OpenTable()` emits lock and `OP_OpenRead`/`OP_OpenWrite` bytecode for a table cursor. For `WITHOUT ROWID` tables it opens the PRIMARY KEY index because that b-tree is the table's canonical storage.
- `sqlite3IndexAffinityStr()`, `computeIndexAffStr()`, `sqlite3TableAffinityStr()`, and `sqlite3TableAffinity()` build or apply affinity/type-check metadata. Strict tables use `OP_TypeCheck`; legacy tables use `OP_Affinity` or attach affinity to the preceding `OP_MakeRecord`.
- `sqlite3ComputeGeneratedColumns()` computes stored and virtual generated columns after normal columns have been loaded and, for inserts, after rowid computation. It marks generated columns as unavailable, walks dependency expressions, detects dependency loops, and reuses `pParse->iSelfTab` so expression code can read the in-progress row.
- `autoIncBegin()`, `sqlite3AutoincrementBegin()`, `autoIncStep()`, and `sqlite3AutoincrementEnd()` manage `AUTOINCREMENT` state through `AutoincInfo` records and four registers per table: table name, current max rowid, `sqlite_sequence` rowid, and original max value.
- `sqlite3MultiValues()` and `sqlite3MultiValuesEnd()` convert multi-row `VALUES` into either a coroutine-backed SELECT or a `UNION ALL` chain. The coroutine form is avoided for WITH clauses, schema parsing, non-constant rows, first-row affinity complications, and special parse modes.
- `sqlite3Insert()` is the main entry point called by the parser. It resolves the destination table, validates the optional column list, chooses one of the insert templates, opens cursors, loads row data, fires triggers, delegates constraint checks, and completes the physical insertion.
- `sqlite3ExprReferencesUpdatedColumn()` supports UPDATE constraint optimization by deciding whether a CHECK or index expression depends on changed columns or changed rowid.
- `sqlite3GenerateConstraintChecks()` is the central shared constraint generator for INSERT and UPDATE. It checks NOT NULL, CHECK, rowid uniqueness, UNIQUE/PRIMARY KEY indexes, UPSERT clauses, REPLACE deletes, generated-column retests, and creates the final table record plus index records in registers.
- `sqlite3SetMakeRecordP5()` records the minimum non-null-trimmable column count for `OP_MakeRecord` when null-trim support is compiled in.
- `sqlite3CompleteInsertion()` emits `OP_IdxInsert` for each generated index record and `OP_Insert` for rowid table data. For `WITHOUT ROWID`, the PRIMARY KEY index is the canonical write.
- `sqlite3OpenTableAndIndices()` allocates and opens the canonical table cursor plus all index cursors, returning cursor bases that callers use consistently with `aRegIdx`.
- `xferCompatibleIndex()`, `xferCompatibleCheck()`, and `xferOptimization()` implement the raw transfer optimization for compatible `INSERT INTO dst SELECT * FROM src` statements.
- Local helper types `IndexIterator` and `IndexListTerm` let constraint checks visit indexes in normal schema order or UPSERT target order.

## Control Flow

`sqlite3Insert()` first normalizes a single-row `VALUES` SELECT into an `ExprList`, resolves the table, authorizes the write, discovers triggers/views, validates read-only status, starts a write operation, and attempts `xferOptimization()` when the statement has no column list, no triggers, and a simple `SELECT *` source.

If raw transfer does not fully handle the statement, insert generation follows four templates:

1. Single-row `VALUES` or `DEFAULT VALUES`: load expressions/defaults directly into the row register block, then write once.
2. Raw transfer optimization: copy table records and index records directly from source b-trees to destination b-trees after strict compatibility checks.
3. `INSERT ... SELECT` where the SELECT does not read the destination: generate a SELECT coroutine and consume each yielded row directly into the destination write path.
4. `INSERT ... SELECT` where triggers exist or the SELECT reads the destination table: first materialize SELECT results into an ephemeral table, then iterate the ephemeral table for writes to avoid read/write interference.

Column preparation tracks storage order carefully. The optional ID list is mapped with `aTabColMap`; generated columns cannot be explicitly inserted into; hidden columns are skipped unless explicitly named where allowed; omitted columns use `sqlite3ColumnExpr()` defaults. INTEGER PRIMARY KEY columns are represented as soft NULL in the record payload while the true rowid is computed separately. Virtual generated columns do not participate in `OP_MakeRecord`; stored generated columns occupy storage slots and are computed later.

Before triggers build a `NEW.*` register array and use `-1` as a placeholder rowid when the final rowid is not yet known. Generated columns and affinity/type checks are applied before trigger execution for real tables. After the main write path, AFTER triggers run, row counters are updated, SELECT loops continue, and top-level code writes back autoincrement state.

## State And Persistence Behavior

Persistent effects are emitted as VDBE operations rather than performed directly. For ordinary rowid tables, `sqlite3GenerateConstraintChecks()` creates the final table record in `aRegIdx[nIdx]`, and `sqlite3CompleteInsertion()` writes secondary indexes with `OP_IdxInsert` followed by table content with `OP_Insert`. Insert flags may include `OPFLAG_NCHANGE`, `OPFLAG_LASTROWID`, `OPFLAG_APPEND`, and `OPFLAG_USESEEKRESULT`.

For `WITHOUT ROWID` tables, the PRIMARY KEY index is the table. `sqlite3OpenTable()` and `sqlite3OpenTableAndIndices()` treat the primary-key index as the canonical data cursor, and `sqlite3CompleteInsertion()` returns after index writes because there is no separate rowid table b-tree.

`AUTOINCREMENT` persistence is staged in registers during row writes. `autoIncStep()` tracks the maximum rowid with `OP_MemMax`; `sqlite3AutoincrementEnd()` updates or inserts the corresponding `sqlite_sequence` row only at top-level statement exit, avoiding updates during VACUUM and rejecting corrupt `sqlite_sequence` schemas.

REPLACE conflict handling may delete existing rows and index entries before writing the new row. If DELETE triggers or foreign-key actions may fire, the code allocates a trigger counter, marks multi-write behavior for statement rollback, and emits uniqueness rechecks after those side effects. This prevents trigger/FK side effects from invalidating earlier uniqueness decisions.

The transfer optimization persists raw records with `OP_RowCell`/`OP_RowData`, `OP_Insert`, and `OP_IdxInsert`, using append and preformatted-record flags when safe. It may generate a runtime empty-destination test; if the destination is not empty, control falls back to the normal insert path.

## Dependencies And Integration Points

This file depends heavily on SQLite internal structures from `sqliteInt.h`: `Parse`, `sqlite3`, `Table`, `Column`, `Index`, `Expr`, `ExprList`, `Select`, `SrcList`, `IdList`, `Upsert`, `Trigger`, `Vdbe`, `VdbeOp`, `Walker`, `AutoincInfo`, and schema/database descriptors.

Major internal integration points include:

- VDBE builders: `sqlite3VdbeAddOp*()`, labels, P4/P5 setters, coroutine setup, cursor open/close, register release, and module comments.
- Parser and resolver state: `sqlite3SrcListLookup()`, `sqlite3ResolveExprListNames()`, `sqlite3ReadSchema()`, `sqlite3BeginWriteOperation()`, `sqlite3NestedParse()`-aware checks, `pParse->iSelfTab`, register allocation, and cleanup hooks.
- Expression and SELECT codegen: `sqlite3ExprCode*()`, `sqlite3ExprIfTrue()`, `sqlite3ExprIfFalseDup()`, `sqlite3Select()`, `SelectDest`, and subquery coroutine metadata.
- Schema metadata: rowid/virtual/view/generated/strict flags, hidden-column flags, default expressions, collations, affinity, primary-key indexes, partial indexes, and expression indexes.
- Constraint and side-effect subsystems: triggers, UPSERT, foreign keys, authorization, preupdate hooks, count-changes, and row-change accounting.
- B-tree/storage semantics exposed through VDBE opcodes such as `OP_OpenWrite`, `OP_NewRowid`, `OP_NoConflict`, `OP_NotExists`, `OP_MakeRecord`, `OP_Insert`, `OP_IdxInsert`, `OP_Delete`, `OP_RowData`, and `OP_RowCell`.

## Risks And Edge Cases

- Register layout is fragile. `regIns`, `regRowid`, `regData`, `regFromSelect`, and `aRegIdx` are deliberately arranged so coroutine outputs, rowid slots, table records, and index records can be reused without copying. Incorrect offsets can corrupt rows or indexes.
- Generated columns require ordered dependency evaluation. The code handles interdependent generated columns through unavailable/busy flags and reports loops; changes here risk false loops, missed recomputation, or stale stored-column values after NOT NULL REPLACE defaults.
- Affinity and strict type checking must occur at exact points. Table records are created during constraint checks to avoid later affinity changes altering persisted data, while strict tables insert `OP_TypeCheck` before `OP_MakeRecord`.
- REPLACE is multi-phase. Deletes, triggers, FK actions, preupdate hooks, and uniqueness rechecks interact; omitting `sqlite3MultiWrite()` or rechecks can leave statement rollback or uniqueness behavior wrong.
- UPSERT index ordering is intentional. Targeted ON CONFLICT clauses are checked before other indexes, and IPK handling may be delayed and resumed around other constraints.
- `WITHOUT ROWID` tables invert assumptions about the data cursor. The primary key index is the data store, and secondary index conflict checks must extract or compare primary-key fields correctly.
- Raw transfer optimization bypasses normal decoding and constraint paths, so compatibility checks must be conservative. The file checks source/destination shape, strict types, generated expressions, hidden columns, affinities, collations, NOT NULL relationships, defaults, indexes, CHECK constraints, foreign keys, authorization, and destination emptiness constraints.
- Virtual table inserts use `OP_VUpdate` and do not support UPSERT here. View inserts rely on triggers and avoid real-table conversion/write paths.
- Compile-time options (`SQLITE_OMIT_*`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_NULL_TRIM`, `SQLITE_ALLOW_ROWID_IN_VIEW`, `SQLITE_TEST`) materially change emitted bytecode and therefore test coverage requirements.

## Test Signals

Useful behavioral tests should cover:

- Single-row `VALUES`, multi-row `VALUES`, `DEFAULT VALUES`, and `INSERT ... SELECT` with both direct coroutine and temp-table paths.
- Self-read inserts such as `INSERT INTO t SELECT ... FROM t` to verify temp-table materialization.
- Column-list mapping with omitted columns, defaults, INTEGER PRIMARY KEY aliases, hidden columns, and generated columns rejected in explicit insert lists.
- Stored and virtual generated columns, including dependencies on rowid/IPK, dependency chains, loop detection, and recomputation after NOT NULL REPLACE defaults.
- STRICT table inserts that should pass/fail `OP_TypeCheck`, plus non-strict affinity behavior and record payload stability.
- `AUTOINCREMENT` inserts, explicit rowids, NULL rowids, trigger-driven inserts, VACUUM behavior, and corrupt/missing `sqlite_sequence`.
- BEFORE, AFTER, and INSTEAD OF triggers, including `NEW.*` rowid placeholder behavior and `RETURNING` on views when compiled with rowid-in-view support.
- NOT NULL, CHECK, rowid, UNIQUE, partial-index, expression-index, and `WITHOUT ROWID` primary-key constraints under ABORT, FAIL, ROLLBACK, IGNORE, REPLACE, and UPSERT DO NOTHING/DO UPDATE.
- REPLACE cases with DELETE triggers, recursive triggers, foreign keys, preupdate hooks, and uniqueness rechecks after side effects.
- Virtual table insert behavior and UPSERT rejection for virtual tables.
- Transfer optimization positive and negative cases: compatible schemas, mismatched indexes/collations/defaults/generated expressions/CHECK constraints, unique-index empty-destination fallback, VACUUM fast paths, authorization checks, and `sqlite3_xferopt_count` in test builds.
