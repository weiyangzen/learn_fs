# sources/storage-engines/sqlite/src/upsert.c

## Purpose
`upsert.c` implements SQLite's `INSERT ... ON CONFLICT ... DO NOTHING/DO UPDATE` support around the `Upsert` AST object. It owns allocation, duplication, target analysis, conflict-target-to-index matching, duplicate-clause handling, and the code-generation bridge that invokes `sqlite3Update()` for the `DO UPDATE` action.

## Important APIs, Types, And Functions
The public functions are `sqlite3UpsertDelete()`, `sqlite3UpsertDup()`, `sqlite3UpsertNew()`, `sqlite3UpsertAnalyzeTarget()`, `sqlite3UpsertNextIsIPK()`, `sqlite3UpsertOfIndex()`, and `sqlite3UpsertDoUpdate()`. They operate mainly on `Upsert`, `Parse`, `SrcList`, `Table`, `Index`, `ExprList`, `Expr`, `NameContext`, and `Vdbe`.

`sqlite3UpsertNew()` records the conflict target, optional partial-index target WHERE clause, SET list, optional action WHERE clause, and next clause. `sqlite3UpsertAnalyzeTarget()` resolves target expressions and binds each targeted clause to a matching unique index or to the rowid/IPK. `sqlite3UpsertOfIndex()` chooses the clause for a failing unique index. `sqlite3UpsertDoUpdate()` locates the conflicting row and delegates the action to `sqlite3Update()`.

## Control Flow
Parsing builds a linked list of `Upsert` objects. Before insert code generation relies on the list, `sqlite3UpsertAnalyzeTarget()` resolves conflict-target symbols against the single insert target table. For each targeted clause, it first recognizes a rowid conflict target on rowid tables. Otherwise it scans unique indexes, requiring the same number of key columns, matching partial-index WHERE expressions when present, and expression/collation/column equivalence between target terms and index key terms. Successful matches set `pUpsertIdx`; redundant clauses for the same index are marked `isDup` for compatibility rather than rejected.

During insert conflict handling, `sqlite3UpsertOfIndex()` returns the first applicable clause for the failed unique index, stopping at an untargeted final clause if present. `sqlite3UpsertNextIsIPK()` helps determine whether later clauses can catch an integer-primary-key conflict while skipping duplicate clauses. For `DO UPDATE`, `sqlite3UpsertDoUpdate()` ensures the data cursor points at the conflicting row: it converts an index cursor to a rowid seek for rowid tables or reads primary-key columns from the failing index and verifies the WITHOUT ROWID table cursor with `OP_Found`. It then duplicates the UPSERT source list, applies REAL affinity to `excluded.*` registers, and calls `sqlite3Update()` with the SET and WHERE expressions.

## State And Persistence Behavior
The `Upsert` list is parse-time state and is freed through `sqlite3UpsertDelete()`, including target lists, partial-index WHERE clauses, SET lists, action WHERE clauses, auxiliary source-list ownership in `pToFree`, and chained clauses. Persistent writes happen only through the INSERT code path and the delegated UPDATE bytecode. Analysis mutates `Upsert` nodes by setting `pUpsertIdx`, `isDoUpdate`, `isDup`, cursor fields supplied by INSERT, source-list fields, and register fields for `excluded.*`.

Matching a conflict target to the wrong index would route persistent conflict handling incorrectly. For expression and partial indexes, the file depends on structural expression comparison rather than SQL text identity. Duplicate conflict clauses are deliberately tolerated to preserve older application behavior even though later duplicates never fire.

## Dependencies And Integration Points
`upsert.c` is tightly coupled to `insert.c`, which builds conflict-checking bytecode and stores cursor/register/source context in `Upsert`. It uses `resolve.c` for target name resolution, `expr.c` for expression duplication and comparison, schema/index metadata from `build.c`, VDBE opcodes for row lookup, and `update.c` for the DO UPDATE action. It also relies on table/index conventions for rowid tables, WITHOUT ROWID primary keys, expression indexes, collations, and partial indexes.

## Risks And Edge Cases
Conflict-target matching is the main risk. Collation wrappers, expression indexes, partial-index predicates, unordered target terms, duplicate ON CONFLICT clauses, rowid aliases, and WITHOUT ROWID primary-key lookup all need exact behavior. `sqlite3UpsertDoUpdate()` must not take ownership of the outer INSERT source list, so it duplicates it before calling `sqlite3Update()`. If the failing unique cursor is not the table cursor, rowid or PK seeking must land on the correct table row or report corruption. REAL affinity on `excluded.*` matters because UPDATE code expects hard REAL values for REAL columns.

## Test Signals
The main signals are `upsert*.test`, especially tests with multiple ON CONFLICT clauses, redundant clauses, partial unique indexes, expression indexes, collations, rowid conflict targets, DO NOTHING fallthrough, DO UPDATE WHERE filters, and WITHOUT ROWID tables. Good secondary signals are `insert*.test`, `indexexpr*.test`, `where*.test` for unique index matching, and corruption/error-path tests expecting "ON CONFLICT clause does not match any PRIMARY KEY or UNIQUE constraint".
