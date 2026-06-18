# sources/storage-engines/sqlite/src/fkey.c

## Purpose

`fkey.c` generates VDBE code and internal trigger programs that implement SQLite foreign key checks and actions. It does not parse `REFERENCES` clauses; instead it consumes `FKey`, `Table`, `Index`, `Parse`, `Expr`, `SrcList`, and `Trigger` structures built by schema and parser code, then emits row-operation checks for INSERT, DELETE, UPDATE, DROP TABLE, and ON UPDATE/ON DELETE actions.

The implementation is omitted when `SQLITE_OMIT_FOREIGN_KEY` is defined, and most code generation is also gated by `SQLITE_OMIT_TRIGGER` because SQLite implements FK actions through trigger-like subprograms.

## Important APIs, Types, And Functions

Public internal entry points are `sqlite3FkLocateIndex()`, `sqlite3FkReferences()`, `sqlite3FkClearTriggerCache()`, `sqlite3FkDropTable()`, `sqlite3FkCheck()`, `sqlite3FkOldmask()`, `sqlite3FkRequired()`, `sqlite3FkActions()`, and `sqlite3FkDelete()`.

`sqlite3FkLocateIndex()` validates that a parent key maps to an INTEGER PRIMARY KEY, PRIMARY KEY index, or UNIQUE index with matching column set and default collations. It returns the parent `Index *` when needed and can allocate an `aiCol` mapping from parent-index order back to child-column indexes.

`sqlite3FkCheck()` is the core DML hook. For child-side modifications it calls `fkLookupParent()` to find the referenced parent row and increments or decrements immediate/deferred FK counters. For parent-side modifications it calls `fkScanChildren()` to scan child rows that reference the parent key and updates counters. `sqlite3FkActions()` invokes cached action triggers built by `fkActionTrigger()` for CASCADE, SET NULL, SET DEFAULT, and RESTRICT.

Helper routines include `exprTableRegister()` and `exprTableColumn()` for building comparison expressions, `fkChildIsModified()` and `fkParentIsModified()` for UPDATE filtering, `isSetNullAction()` for avoiding redundant checks inside SET NULL action triggers, and `fkTriggerDelete()` for freeing cached trigger structures.

## Control Flow

Foreign key enforcement uses counters. Deferred constraints update the database-handle deferred counter and are checked at transaction commit. Immediate constraints usually update a statement-level counter and abort at statement end; single-row immediate INSERT can halt immediately because no statement transaction is opened.

For child INSERT/UPDATE-new-row paths, `sqlite3FkCheck()` locates the parent table and key index, opens the parent table or unique index, skips enforcement when any child key column is NULL, applies parent affinity, and emits `OP_NotExists` or `OP_Found` checks. Missing parent rows increment the proper FK counter or halt immediately in the single-row case. For child DELETE/UPDATE-old-row paths, the same lookup decrements counters when removing a row that had represented an outstanding violation.

For parent DELETE/UPDATE-old-row paths, `fkScanChildren()` builds a WHERE clause equating parent key register values to child key columns, resolves it against a `SrcList` for the child table, runs `sqlite3WhereBegin()`, and emits `OP_FkCounter` for each child row found. Self-referential FKs add terms to exclude the current row. For parent INSERT/UPDATE-new-row paths, scans may decrement counters for now-satisfied deferred violations.

`fkActionTrigger()` lazily synthesizes a `Trigger` containing one step: SELECT RAISE for RESTRICT, DELETE for ON DELETE CASCADE, or UPDATE for CASCADE/SET NULL/SET DEFAULT update-style actions. The trigger gets cached in `FKey.apTrigger[delete/update]` and reused until schema changes call `sqlite3FkClearTriggerCache()`.

`sqlite3FkDropTable()` emits a trigger-disabled `DELETE FROM <table>` before schema removal when FK checks require it, then verifies immediate counter zero before allowing schema changes that cannot be rolled back by a statement transaction.

## State And Persistence Behavior

The file does not persist data directly; it emits VDBE programs that read and modify table contents and update runtime FK counters. Persistent FK metadata lives in schema objects and `Schema.fkeyHash`, which maps parent table names to linked lists of child `FKey` objects. Cached action triggers are in-memory members of `FKey` and are freed on schema invalidation or FK deletion. `sqlite3FkDelete()` removes FKs from `fkeyHash`, frees cached triggers, and frees the `FKey` objects when a table schema object is destroyed.

## Dependencies And Integration Points

This code is tightly integrated with the parser/code generator (`Parse`, `NameContext`, expression builders), VDBE opcodes (`OP_FkCounter`, `OP_FkIfZero`, `OP_Found`, `OP_NotExists`, `OP_MustBeInt`, `OP_Halt` via `sqlite3HaltConstraint()`), the schema layer (`Table`, `Index`, `Schema.fkeyHash`), the WHERE planner (`sqlite3WhereBegin()`/`sqlite3WhereEnd()`), table locking, authorizer callbacks, trigger subprogram execution, and database flags such as `SQLITE_ForeignKeys`, `SQLITE_DeferFKs`, and `SQLITE_FkNoAction`.

## Risks

Correctness depends on exact parent-key matching rules: partial indexes, expression indexes, non-unique indexes, and mismatched collations must not satisfy FK parent requirements. UPDATE filtering via `aChange` and rowid handling must not skip changed parent or child keys. Self-referential constraints are high risk because the code must avoid counting the row against itself while still detecting other rows. DROP TABLE behavior is delicate because schema changes are not always statement-rollbackable. Cached triggers must be cleared on schema changes or they may refer to stale table/column metadata. Authorization `SQLITE_IGNORE` intentionally treats parent columns as NULL-like, which can affect generated checks.

## Test Signals

Strong signals include SQLite FK test suites covering immediate and deferred constraints, composite keys, INTEGER PRIMARY KEY parent keys, WITHOUT ROWID tables, self-referential FKs, ON UPDATE/DELETE CASCADE, SET NULL, SET DEFAULT, RESTRICT, `PRAGMA defer_foreign_keys`, `PRAGMA foreign_keys`, DROP TABLE with dependent constraints, missing parent tables during DROP, and foreign key mismatch diagnostics. Tests should also stress OOM during `aiCol` allocation and trigger synthesis, authorizer `SQLITE_IGNORE`, generated columns with SET DEFAULT, and schema invalidation after ALTER TABLE.
