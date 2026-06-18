# sources/storage-engines/sqlite/src/whereInt.h

## Purpose

`whereInt.h` is the private interface for SQLite's WHERE-clause planner and loop code generator. It is shared by the WHERE subsystem source files, especially `where.c`, `wherecode.c`, and `whereexpr.c`, and defines the in-memory model used to decompose expressions, enumerate candidate scan loops, choose a path, and emit VDBE loop bytecode.

The header intentionally keeps these definitions out of the public API. Its types are tightly coupled to parser state (`Parse`), source lists (`SrcList`/`SrcItem`), expression trees (`Expr`, `ExprList`, `Select`), schema metadata (`Table`, `Index`), estimated costs (`LogEst`), bitmask dependency tracking (`Bitmask`), and VDBE cursors/opcodes.

## Important APIs, types, and flags

- `WhereInfo` is the top-level WHERE planning/codegen state returned by `sqlite3WhereBegin()` and consumed by `sqlite3WhereEnd()`. It owns the `WhereClause`, `WhereMaskSet`, selected `WhereLoop` list, per-level `WhereLevel` array, loop labels, distinct/order metadata, one-pass state, deferred-seek flag, star-query flags, and memory cleanup chain.
- `WhereLevel` is the emitted-loop implementation record for one FROM item. It stores table/index cursors, break/continue/body labels, skip-scan and LIKE/big-null state, Bloom filter register, optional `WhereRightJoin`, selected `WhereLoop`, `notReady` dependency mask, and loop terminator opcode operands.
- `WhereLoop` represents a candidate or selected scan algorithm. It carries dependency masks, cost estimates (`rSetup`, `rRun`, `nOut`), table position, sort-order contribution, btree or virtual-table details, `wsFlags`, and the `WhereTerm` array that drives constraints.
- `WherePath` is the solver path abstraction: a sequence of `WhereLoop`s with accumulated row/cost/order information.
- `WhereTerm` represents one analyzed WHERE subexpression. It records the original expression, operator mask (`WO_*`), flags (`TERM_*`), parent/child virtual-term relationships, cursor/column on the left side, prerequisites, truth probability, OR/AND subclause info, vector field index, and virtual-table match operator.
- `WhereClause` owns an array of `WhereTerm`s split by `AND` or `OR`. It also tracks `nBase` so original terms can be distinguished from optimizer-created virtual terms.
- `WhereScan` is a term iterator used by planner code to find compatible constraints, including equivalence-class columns.
- `WhereMaskSet` maps sparse VDBE cursor ids to dense `Bitmask` bits so prerequisite and dependency sets fit in fixed-width masks.
- `WhereLoopBuilder` is the shared state used while proposing loops, including STAT4 probe state and planner combination limit controls.
- `WhereOrCost` and `WhereOrSet` keep the best few OR-branch alternatives.
- `WhereRightJoin` stores the extra cursors/registers/subroutine addresses needed to implement unmatched-row processing for RIGHT JOIN.
- `WhereMemBlock` tracks allocations attached to a `WhereInfo` lifetime via `sqlite3WhereMalloc()` and `sqlite3WhereRealloc()`.

The header also defines the planner-facing operator masks:

- `WO_EQ`, `WO_LT`, `WO_LE`, `WO_GT`, `WO_GE`, `WO_IN`, `WO_IS`, `WO_ISNULL` for ordinary indexable terms.
- `WO_OR` and `WO_AND` for decomposed compound terms.
- `WO_EQUIV` for transitive equivalence, `WO_ROWVAL` for vector/row-value slices, `WO_AUX` for virtual-table-only operators, and `WO_NOOP`.

`WhereLoop.wsFlags` drive code-generation selection:

- Constraint shape: `WHERE_COLUMN_EQ`, `WHERE_COLUMN_RANGE`, `WHERE_COLUMN_IN`, `WHERE_COLUMN_NULL`, `WHERE_TOP_LIMIT`, `WHERE_BTM_LIMIT`.
- Access strategy: `WHERE_IPK`, `WHERE_INDEXED`, `WHERE_IDX_ONLY`, `WHERE_VIRTUALTABLE`, `WHERE_MULTI_OR`, `WHERE_AUTO_INDEX`, `WHERE_SKIPSCAN`, `WHERE_IN_SEEKSCAN`.
- Semantics and optimizations: `WHERE_ONEROW`, `WHERE_PARTIALIDX`, `WHERE_IN_EARLYOUT`, `WHERE_BIGNULL_SORT`, `WHERE_TRANSCONS`, `WHERE_BLOOMFILTER`, `WHERE_SELFCULL`, `WHERE_OMIT_OFFSET`, `WHERE_COROUTINE`, `WHERE_EXPRIDX`.

## Control flow and state model

The state model is deliberately split into analysis, planning, and codegen phases:

1. `whereexpr.c` initializes and fills `WhereClause` with `WhereTerm`s, splitting the SQL WHERE tree, deriving virtual terms, computing dependency masks, and setting `WO_*`/`TERM_*`.
2. Planner code in `where.c` uses `WhereLoopBuilder`, `WhereScan`, `WhereLoop`, `WhereOrSet`, and `WherePath` to enumerate scan choices and choose loop order.
3. `wherecode.c` consumes the selected `WhereInfo.a[]` `WhereLevel`s and `WhereLoop`s to emit VDBE opcodes for table/index/virtual-table loops, IN loops, skip scans, OR subplans, Bloom filters, and outer joins.
4. `sqlite3WhereEnd()` uses the `WhereLevel` fields populated during start-code generation to close loops, resolve labels, emit unmatched outer-join rows, and release WHERE-owned memory.

`WhereTerm` parent-child flags are central. Optimizer-created children such as BETWEEN bounds, LIKE range constraints, transitive/commuted terms, and vector slices can mark original terms as already satisfied when all children are coded. Conversely, an original term can remain available as a correctness check if children are only range approximations.

Dependency masks are the other central control mechanism. `prereqRight`, `prereqAll`, `notReady`, `maskSelf`, and `prereq` prevent terms from being evaluated before all referenced FROM items are available and prevent ON-clause constraints from being incorrectly pushed across outer joins.

## State and persistence behavior

All state described here is transient planning/code-generation state for one SQL statement. It does not persist to the database. Persistence-like effects are limited to:

- VDBE bytecode emitted into the current prepared statement.
- Planner memory allocations attached to `WhereInfo.pMemToFree`.
- Temporary VDBE cursors/registers for rowsets, ephemeral indexes, Bloom filters, IN RHS materialization, RIGHT JOIN match tracking, and auto indexes.
- Optional scanstatus and EXPLAIN metadata embedded in VDBE opcodes.

The header's memory ownership signals are important. `TERM_DYNAMIC` means `WhereClauseClear()` must delete the expression. `TERM_ORINFO`/`TERM_ANDINFO` mean nested clauses must be recursively cleared. `WhereLoop.u.vtab.needFree` indicates ownership of `idxStr` returned by virtual-table planning.

## Dependencies and integration points

The header depends on core SQLite internal definitions from `sqliteInt.h`, including `Parse`, `SrcList`, `Expr`, `ExprList`, `Select`, `Index`, `Table`, `Vdbe`, `Bitmask`, `LogEst`, and many opcode/token/join constants. It integrates with:

- `whereexpr.c`: `sqlite3WhereClauseInit()`, `sqlite3WhereSplit()`, `sqlite3WhereExprAnalyze()`, usage-mask helpers, table-valued-function argument conversion, and LIMIT/OFFSET virtual-table constraints.
- `wherecode.c`: EXPLAIN text, scanstatus, loop-start bytecode emission, RIGHT JOIN unmatched-row loop generation.
- `where.c` and related planner files: mask lookup, term search, loop enumeration, loop printing, memory management, chosen path construction.
- VDBE: cursor ids, labels, registers, opcode operands, scanstatus ranges, `OP_Explain`, `OP_Filter`, `OP_DeferredSeek`, `OP_Next`/`OP_Prev`, and join subroutines.
- Virtual table API: `sqlite3_index_constraint` operator values are intentionally aligned with selected `WO_*` values and stored in `WhereLoop.u.vtab`.

## Risks and edge cases

- Bitmask width limits join size. `WhereMaskSet` compresses cursor ids, but the number of simultaneously tracked FROM terms is still bounded by `Bitmask` width.
- `WhereLevel` is both a codegen scratchpad and a contract with `sqlite3WhereEnd()`. Incorrect label/opcode fields can produce malformed VDBE control flow.
- Parent-child `TERM_*` state is correctness-critical for LIKE, BETWEEN, vector comparisons, and outer joins. Premature `TERM_CODED` can drop required runtime checks.
- `WO_*` values intentionally match virtual-table constraint constants for equality/range operators. Changing token or mask ordering can silently break xBestIndex integration.
- RIGHT JOIN and LEFT JOIN markings interact with prerequisite masks and `WhereRightJoin`; constraints must not be pushed to the wrong side of an outer join.
- `WHERE_IDX_ONLY`, `WHERE_MULTI_OR`, deferred seek, and covering-index fields determine whether table cursors are read. Mistakes can read stale/null rows or miss needed columns.
- `WhereLoop` copy boundaries such as `WHERE_LOOP_XFER_SZ` are fragile when fields are inserted.
- STAT4, scanstatus, WHERETRACE, virtual-table, LIKE, OR optimization, and window-function compile-time options create many conditional structure fields and behavioral paths.

## Test signals

Useful test coverage should include:

- EXPLAIN QUERY PLAN strings for rowid, covering-index, expression-index, partial-index, virtual-table, automatic-index, skip-scan, multi-index OR, and Bloom-filter scans.
- WHERE terms involving BETWEEN, LIKE/GLOB prefixes, vector equality, vector IN, `IS NULL`, `IS`, transitive equality, collations, expression indexes, and generated virtual terms.
- LEFT, RIGHT, and mixed outer joins with ON/WHERE constraints that can and cannot be pushed down.
- Virtual-table `xBestIndex` constraints for MATCH/LIKE/GLOB/REGEXP, `!=`, `IS NOT`, `NOT NULL`, LIMIT, OFFSET, and IN handling.
- Large joins near `Bitmask` capacity.
- OOM/fault-injection runs around `WhereClause` growth, `WhereLoop` allocation, vtab `idxStr`, and OR/AND nested clause allocation.
