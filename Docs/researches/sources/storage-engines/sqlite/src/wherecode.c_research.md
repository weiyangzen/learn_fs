# sources/storage-engines/sqlite/src/wherecode.c

## Purpose

`wherecode.c` emits the VDBE bytecode that implements the query plan selected by SQLite's WHERE planner. It is the code-generation half of the WHERE subsystem: planner analysis chooses `WhereLoop`s and loop order, then this file turns each selected `WhereLevel` into concrete cursor seeks, scans, constraint checks, IN loops, virtual-table calls, Bloom-filter checks, OR subplans, deferred seeks, and outer-join bookkeeping.

The file also owns WHERE-loop EXPLAIN text and scanstatus instrumentation. It was split from `where.c` so planner enumeration and bytecode generation could evolve independently.

## Important APIs and functions

Public-to-the-WHERE-subsystem entry points:

- `sqlite3WhereExplainOneScan()` optionally emits an `OP_Explain` for a scan loop and returns its address.
- `sqlite3WhereExplainBloomFilter()` emits an `OP_Explain` describing a Bloom filter.
- `sqlite3WhereAddExplainText()` fills an existing `OP_Explain` P4 string with `SCAN`/`SEARCH`, table name, index name, rowid range, virtual-table index, LEFT-JOIN marker, and optional row estimate.
- `sqlite3WhereAddScanStatus()` records `sqlite3_stmt_scanstatus()` metadata and cursor address ranges.
- `sqlite3WhereCodeOneLoopStart()` is the main loop-start generator for one `WhereLevel`.
- `sqlite3WhereRightJoinLoop()` emits the second pass that outputs unmatched RHS rows for RIGHT JOIN.

Important internal helpers:

- `disableTerm()` marks a `WhereTerm` or its parent as coded, while respecting LEFT OUTER JOIN ON/WHERE semantics and LIKE two-pass checks.
- `codeApplyAffinity()` trims no-op affinity bytes and emits `OP_Affinity`.
- `updateRangeAffinityStr()` suppresses affinity changes that are unnecessary or unsafe for range RHS values.
- `removeUnindexableInClauseTerms()` rewrites vector `IN (SELECT...)` expressions to only the components usable by the selected index.
- `codeINTerm()` materializes or opens an IN RHS and sets up `WhereLevel.u.in.aInLoop`.
- `codeEqualityTerm()` evaluates equality, `IS NULL`, or IN constraints into registers and disables terms where safe.
- `codeAllEqualityTerms()` allocates key registers, handles skip-scan prefixes, evaluates equality constraints, and returns index affinity text.
- `whereLikeOptimizationStringFixup()` supports two-pass LIKE optimization when BLOBs can match LIKE.
- Cursor-hint helpers under `SQLITE_ENABLE_CURSOR_HINTS` build `OP_CursorHint` expressions that can be safely pushed to btree cursors.
- `codeDeferredSeek()` emits `OP_DeferredSeek` and optional column map data for OR/RIGHT-JOIN read avoidance.
- `codeExprOrVector()` evaluates scalar or vector RHS expressions into registers.
- `whereApplyPartialIndexConstraints()` marks WHERE terms implied by a partial index predicate as coded.
- `filterPullDown()` evaluates available inner Bloom filters before an outer index lookup.
- `whereLoopIsOneRow()` detects unique index equality scans that produce at most one row per IN key.

## Main control flow

`sqlite3WhereCodeOneLoopStart()` is the center of the file. It receives `pWInfo`, `iLevel`, `pLevel`, and a `notReady` mask, initializes break/continue/IN labels, detects reverse scan order from `revMask`, initializes LEFT JOIN match registers, and then dispatches by selected loop strategy:

1. Coroutine subquery: emits `OP_InitCoroutine` and `OP_Yield`, then records `OP_Goto` as the loop terminator.
2. Virtual table: evaluates xFilter constraints into a register block, handles virtual-table IN constraints either through `OP_VInitIn` or generated IN loops, emits `OP_VFilter`, sets up `OP_VNext`, reloads IN values that xFilter might mutate, and optionally emits post-filter equality checks for IN terms not handled by the virtual table.
3. Rowid equality/IN (`WHERE_IPK` with equality or IN): evaluates the rowid key, optionally checks a Bloom filter, emits `OP_SeekRowid`, and uses no iterative step.
4. Rowid range: computes start/end rowid bounds, emits `OP_SeekGT`/`OP_SeekGE`/`OP_SeekLT`/`OP_SeekLE` or full rewind/last, emits end-bound checks, and records `OP_Next`/`OP_Prev`.
5. Indexed btree scan: computes equality and range key registers, handles skip-scan, LIKE range two-pass setup, NULLS FIRST/LAST big-null scan, Bloom filters, `OP_SeekScan`, start seek, end-bound opcodes, deferred table seek or WITHOUT ROWID primary-key lookup, partial-index term elimination, and loop terminator selection.
6. Multi-index OR: recursively calls `sqlite3WhereBegin()` for each OR branch, uses `RowSetTest` for rowid tables or an ephemeral primary-key index for WITHOUT ROWID tables to suppress duplicates, invokes the main loop body via `OP_Gosub`, tracks a possible covering index, and propagates untested-term/deferred-seek state.
7. Full scan: emits `OP_Rewind`/`OP_Last` and `OP_Next`/`OP_Prev`, except recursive pseudo-cursors which need no iteration opcodes.

After opening/seeking the loop, the function emits residual WHERE-term tests in up to three passes: terms covered by the index first, then remaining terms without correlated subqueries, then correlated-subquery terms. It then emits transitive-equivalence checks that are not otherwise usable because a referenced table is not ready. Finally it records RIGHT JOIN matches, LEFT JOIN hits, and creates the RIGHT JOIN interior subroutine when needed.

`sqlite3WhereRightJoinLoop()` is a later second-pass generator. It nulls all tables to the left of the RIGHT JOIN, builds a single-table scan over the RHS, filters out rows already recorded in `WhereRightJoin.iMatch`/`regBloom`, and invokes the stored subroutine for unmatched rows.

## State and persistence behavior

This file mutates transient compilation state and emits persistent prepared-statement bytecode:

- `Parse.nMem` and `Parse.nTab` are incremented for registers and cursors used by constraints, rowsets, ephemeral indexes, Bloom filters, and subroutines.
- `WhereLevel` fields are populated with VDBE addresses (`addrBrk`, `addrCont`, `addrNxt`, `addrSkip`, `addrBody`, `addrFirst`, `addrBignull`), loop terminator opcode operands, IN-loop arrays, LIKE counters, Bloom filter registers, and scanstatus visit addresses.
- `WhereTerm.wtFlags` is changed with `TERM_CODED` and `TERM_LIKECOND` to avoid redundant or unsafe residual checks.
- `WhereInfo.bDeferredSeek` is set when generated code uses deferred table seeks.
- `WhereRightJoin` match structures are populated through generated VDBE operations (`OP_IdxInsert`, `OP_FilterAdd`, `OP_Filter`, `OP_Found`) at runtime.
- VDBE bytecode becomes part of the prepared statement and is later executed by the VM. No database file state is changed during compilation.

Runtime temporary state emitted by this file includes IN RHS cursors, RowSet registers, ephemeral duplicate-suppression indexes, Bloom filter registers, LEFT JOIN match flags, and RIGHT JOIN match indexes.

## Dependencies and integration points

`wherecode.c` depends heavily on structures and flags from `whereInt.h` and the rest of SQLite internals:

- Planner input: `WhereInfo`, `WhereLevel`, `WhereLoop`, `WhereTerm`, `WhereClause`, `WhereRightJoin`.
- Expression/codegen APIs: `sqlite3ExprCode*()`, `sqlite3ExprIfFalse()`, `sqlite3ExprCompare()`, `sqlite3ExprCoveredByIndex()`, `sqlite3CodeRhsOfIN()`, `sqlite3FindInIndex()`.
- VDBE APIs: `sqlite3VdbeAddOp*()`, labels, coverage annotations, P4 ownership, `sqlite3VdbeScanStatus*()`, `sqlite3VdbeNoJumpsOutsideSubrtn()`.
- Planner recursion: `sqlite3WhereBegin()`, `sqlite3WhereEnd()`, `sqlite3WhereContinueLabel()`, and `sqlite3WhereUsesDeferredSeek()` for OR subplans and RIGHT JOIN unmatched scans.
- Schema and storage metadata: rowid vs WITHOUT ROWID tables, primary-key indexes, covering indexes, expression indexes, partial indexes, collations, affinity strings, sort-order flags.
- Virtual-table integration: xBestIndex output stored in `WhereLoop.u.vtab`, `OP_VFilter`, `OP_VNext`, `OP_VInitIn`, omitted constraints, `idxNum`, `idxStr`, LIMIT/OFFSET omission.
- Conditional features: `SQLITE_OMIT_EXPLAIN`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_LIKE_DOESNT_MATCH_BLOBS`, `SQLITE_ENABLE_CURSOR_HINTS`, `SQLITE_OMIT_OR_OPTIMIZATION`.

## Risks and edge cases

- Outer join semantics are fragile. `disableTerm()`, residual term passes, cursor hints, partial-index implication, and RIGHT JOIN subroutines all need to distinguish ON terms from WHERE terms and LEFT/RIGHT/JT_LTORJ positions.
- Term disabling is an optimization with correctness consequences. Transitive constraints, LIKE range children, partial-index predicates, and virtual-table omitted constraints must only suppress checks when logically guaranteed.
- IN-loop state is spread across generated opcodes and `WhereLevel.u.in.aInLoop`; multi-column vector IN and virtual-table IN reloads are particularly sensitive to register and cursor ordering.
- Range seek opcodes depend on token ordering and reverse-order/sort-order swaps. Mistakes lead to off-by-one range inclusion errors.
- LIKE optimization may require two passes when BLOBs can match; the loop counter is packed into `iLikeRepCntr` and later affects `OP_String8` P3/P5 and residual LIKE evaluation.
- Big-null sort handling splits NULL and non-NULL scans and interacts with LEFT JOIN match flags.
- Bloom-filter pull-down clears `regFilter` after moving the check; doing so too early or with incorrect dependencies can skip valid rows.
- Deferred seek and covering-index logic can avoid table reads only when all later consumers can read from the index or tolerate null-row state.
- Recursive multi-index OR planning must avoid pushing down subqueries, row-value slices, or outer-join ON terms incorrectly.
- Virtual-table `OP_VFilter` P4 ownership and `idxStr` nulling after OOM avoid double-free/use-after-free issues; this path needs fault-injection coverage.

## Test signals

Good regression tests should inspect both results and generated plans:

- `EXPLAIN QUERY PLAN` for `SCAN`, `SEARCH`, covering indexes, rowid ranges, expression indexes, partial indexes, auto indexes, virtual-table indexes, multi-index OR, Bloom filters, LEFT JOIN, and RIGHT JOIN.
- Bytecode-level tests for `OP_SeekRowid`, `OP_SeekGE`/`LE`, `OP_IdxGT`/`GE`, `OP_SeekScan`, `OP_DeferredSeek`, `OP_CursorHint`, `OP_VFilter`, `OP_RowSetTest`, `OP_Filter`, and `OP_FilterAdd`.
- Query result tests for equality/range scans, reverse scans, skip scans, IN and vector IN, LIKE/GLOB prefixes, NULLS FIRST/LAST order, WITHOUT ROWID tables, expression and partial indexes.
- Multi-index OR tests with duplicate row suppression, outer joins, subqueries, row-value comparisons, covering-index eligibility, and `WHERE_DUPLICATES_OK`.
- Virtual-table tests for omitted constraints, handled and unhandled IN constraints, LIMIT/OFFSET pushdown, `idxStr` lifetime, and OFFSET counter zeroing.
- RIGHT JOIN tests with matched and unmatched rows, additional WHERE constraints, indexes on RHS, coroutines to the left, Bloom false positives, and WITHOUT ROWID RHS tables.
- OOM/fault-injection tests around vector-IN rewrite, IN-loop array allocation, `idxStr`, OR subplan SrcList allocation, scanstatus/explain strings, and deferred-seek column maps.
