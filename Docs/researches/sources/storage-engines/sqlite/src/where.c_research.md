# Research: sources/storage-engines/sqlite/src/where.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008807`: lines 1-6955, `Docs/researches/chunks/subset-b-008807_research.md`
- `subset-b-008808`: lines 6956-7886, `Docs/researches/chunks/subset-b-008808_research.md`

## Chunk Research

### subset-b-008807: lines 1-6955

# sources/storage-engines/sqlite/src/where.c lines 1-6955

## Scope

This chunk covers the opening and most of the query-planner implementation in SQLite's `where.c`, from the module header through the first half of `sqlite3WhereBegin()`. It includes WHERE result accessors, term scanning, automatic index and Bloom-filter construction, virtual-table `xBestIndex` integration, STAT4 selectivity estimators, `WhereLoop` candidate management, B-tree and virtual-table loop generation, OR optimization, ORDER BY/GROUP BY/DISTINCT satisfaction analysis, path solving, join-omission and Bloom-filter heuristics, indexed-expression support, reverse-scan setup, and initialization of the `WhereInfo` object. The range ends at line 6955 inside the special no-FROM-clause branch of `sqlite3WhereBegin()`, before the rest of planning/code generation and `sqlite3WhereEnd()`.

## Purpose

- Generate and cost candidate access paths for SQL WHERE processing, making this file the central query optimizer for SELECT, UPDATE, DELETE, and related statement forms.
- Represent each possible table access method as a `WhereLoop`, including rowid lookup, index lookup, full scans, covering-index scans, skip-scan, automatic indexes, multi-index OR scans, and virtual-table scans.
- Estimate row counts and run costs using `sqlite_stat1`, optional STAT4 samples, likelihood hints, index shape, row width, ORDER BY sorting cost, and planner heuristics.
- Choose a low-cost nested-loop join order while considering join-order barriers from CROSS/outer joins, ORDER BY/GROUP BY/DISTINCT requirements, one-pass update/delete eligibility, and optimizer limits.
- Bridge SQLite's internal WHERE analysis to virtual table APIs by building `sqlite3_index_info`, exposing hidden planner metadata to `sqlite3_vtab_collation()`, `sqlite3_vtab_in()`, `sqlite3_vtab_rhs_value()`, and `sqlite3_vtab_distinct()`.
- Prepare state used later by bytecode generation, including `WhereInfo`, `WhereLevel`, loop labels, reverse-scan masks, indexed-expression substitution lists, autoindex descriptors, Bloom-filter flags, and planner debug traces.

## Important APIs, Types, And Functions

- `HiddenIndexInfo` is private storage placed immediately after `sqlite3_index_info`. It records the `WhereClause`, `Parse`, distinctness mode, IN-constraint masks, and cached RHS `sqlite3_value` objects for virtual-table helper APIs.
- `sqlite3WhereOutputRowCount()`, `sqlite3WhereIsDistinct()`, `sqlite3WhereIsOrdered()`, `sqlite3WhereIsSorted()`, `sqlite3WhereContinueLabel()`, `sqlite3WhereBreakLabel()`, `sqlite3WhereOkOnePass()`, and `sqlite3WhereUsesDeferredSeek()` expose planner results to other compiler stages.
- `sqlite3WhereOrderByLimitOptLabel()` and `sqlite3WhereMinMaxOptEarlyOut()` provide jump-label decisions for ORDER BY LIMIT and min/max early-out optimizations once selected loops prove useful ordering.
- `WhereScan`, `whereScanInit()`, `whereScanNext()`, and `sqlite3WhereFindTerm()` iterate WHERE terms matching a table column or index column. They handle affinity, collation, expression indexes, transitive equality via `WO_EQUIV`, vector IN fields, and outer-join restrictions.
- `WhereOrSet`, `whereOrInsert()`, and `whereOrMove()` keep the bounded best cost/prerequisite combinations used when estimating OR-subterm plans.
- `sqlite3WhereGetMask()`, `createMask()`, `sqlite3WhereMalloc()`, and `sqlite3WhereRealloc()` manage planner bitmasks and `WhereInfo`-owned temporary memory.
- `isDistinctRedundant()` proves when a DISTINCT list is unnecessary by matching the result columns and equality constraints against a unique, non-partial, non-null index.
- `translateColumnToCopy()` rewrites previously emitted VDBE `OP_Column` or `OP_Rowid` opcodes to `OP_Copy`, `OP_Sequence`, or `OP_Null` when an automatic index is built over a coroutine source.
- `constraintCompatibleWithOuterJoin()` centralizes which ON-clause terms are safe to use for LEFT, RIGHT, and left-to-right join transformations.
- `termCanDriveIndex()`, `columnIsGoodIndexCandidate()`, and `constructAutomaticIndex()` identify equality terms that can drive an automatic transient covering index, allocate the `Index` object, emit `OP_OpenAutoindex`, fill it, optionally build a Bloom filter, and record the corresponding `WhereLoop`.
- `sqlite3ConstructBloomFilter()` emits bytecode to populate a Bloom-filter blob from a selected inner table and can pull down additional eligible Bloom filters for later loops.
- `allocateIndexInfo()`, `freeIndexInfo()`, `vtabBestIndex()`, `whereLoopAddVirtualOne()`, and `whereLoopAddVirtual()` implement virtual-table planning. They convert internal `WhereTerm` and ORDER BY state into `sqlite3_index_info`, call `xBestIndex`, validate its outputs, and create virtual-table `WhereLoop` candidates.
- `sqlite3_vtab_collation()`, `sqlite3_vtab_in()`, `sqlite3_vtab_rhs_value()`, `sqlite3_vtab_distinct()`, and `sqlite3VtabUsesAllSchemas()` are exported helper APIs used by virtual-table modules while their `xBestIndex()` callback is running.
- STAT4 helpers such as `whereKeyStats()`, `whereRangeSkipScanEst()`, `whereRangeScanEst()`, `whereEqualScanEst()`, and `whereInScanEst()` refine estimates for equality, IN-list, range, and skip-scan plans using histogram samples when available.
- Debug helpers `sqlite3WhereTermPrint()`, `sqlite3WhereClausePrint()`, `sqlite3WhereLoopPrint()`, `sqlite3ShowWhereLoop()`, and `sqlite3ShowWhereLoopList()` support `WHERETRACE` and debug builds.
- `whereLoopInit()`, `whereLoopClearUnion()`, `whereLoopClear()`, `whereLoopResize()`, `whereLoopXfer()`, `whereLoopDelete()`, and `whereInfoFree()` own dynamic memory for loop candidates, virtual-table `idxStr`, autoindex `Index` objects, and planner allocations.
- `whereLoopFindLesser()`, `whereLoopCheaperProperSubset()`, `whereLoopAdjustCost()`, and `whereLoopInsert()` maintain the global candidate list, pruning dominated loops and nudging subset/superset costs so more constrained paths remain preferable.
- `whereLoopOutputAdjust()`, `estLikePatternLength()`, and `exprNodePatternLengthEst()` reduce output-row estimates for unused filtering terms, likelihood hints, equality heuristics, and LIKE/GLOB-style pattern length.
- `whereRangeVectorLen()` validates how many columns of a vector inequality can be used by an index range scan.
- `whereLoopAddBtreeIndex()` recursively extends a B-tree loop across equality, IN, IS NULL, range, LIKE range, vector range, and skip-scan constraints, updating `wsFlags`, `nEq`, `nBtm`, `nTop`, `nSkip`, prerequisites, cost, and row-count estimates.
- `whereLoopAddBtree()` generates all B-tree-table candidates, including fake rowid primary-key loops, automatic indexes, full table scans, covering/non-covering index scans, partial-index eligibility, and constrained index searches.
- `whereLoopAddOr()` creates `WHERE_MULTI_OR` candidates by planning each OR branch independently and combining the bounded best costs.
- `whereLoopAddAll()` walks FROM items left-to-right to create candidates for every table while enforcing CROSS JOIN, LEFT/RIGHT/FULL JOIN, EXISTS-to-JOIN, and virtual-table unusable-term constraints.
- `wherePathMatchSubqueryOB()` and `wherePathSatisfiesOrderBy()` determine whether candidate loop prefixes satisfy ORDER BY, GROUP BY, DISTINCT, min/max, ORDER BY LIMIT, virtual-table ordering, subquery ORDER BY, reverse scan, nulls-first/last, collation, expression-index, and unique-order-distinct rules.
- `whereSortingCost()`, `computeMxChoice()`, `whereLoopIsNoBetter()`, `wherePathSolver()`, and `whereInterstageHeuristic()` implement bounded dynamic-programming join-order selection, sorting-cost comparison, star-schema scan-cost adjustment, and a second-pass guard against replacing selective searches with full scans just to avoid sorting.
- `whereShortCut()` handles the common single-table unique lookup or rowid lookup without running the full planner.
- `exprIsDeterministic()`, `whereOmitNoopJoin()`, `whereCheckIfBloomFilterIsUseful()`, `whereAddIndexedExpr()`, and `whereReverseScanOrder()` implement auxiliary planner passes for deterministic expression checks, removable LEFT JOINs, Bloom-filter marking, indexed-expression substitution, and reverse unordered select behavior.
- `sqlite3WhereBegin()` begins the public WHERE planning/codegen entry point. In this chunk it validates flags, disables impossible ORDER BY optimization with too many terms, enforces the table-bitmask limit, allocates and initializes `WhereInfo`, initializes the builder and `WhereClause`, splits the WHERE expression on AND, and starts the no-FROM special case.

## Control Flow

The planner first exposes simple `WhereInfo` result accessors and utility functions used by later code-generation stages. It then builds the scanning machinery that finds useful `WhereTerm` objects. `whereScanInit()` maps requested table/index columns through real table columns, rowid, or expression-index expressions. `whereScanNext()` advances through the current and outer `WhereClause` objects, expands transitive equalities into equivalence lists, enforces collation and affinity compatibility, avoids unusable outer-join propagated terms, and returns only operators matching the requested `WO_*` mask.

Automatic-index planning begins by screening terms with `termCanDriveIndex()`. If a term is an equality or IS constraint on the current table, has no unavailable prerequisites, is compatible with outer joins and column affinity, and is not already an unsuitable index candidate, it may become an autoindex key. `constructAutomaticIndex()` later builds the transient covering index, includes extra columns required by the query, handles WITHOUT ROWID primary-key columns, fills the index from a table scan or coroutine, applies partial-index predicates, emits Bloom-filter inserts when useful, and rewrites earlier column reads for coroutine sources.

Virtual-table planning has a separate flow. `allocateIndexInfo()` collects usable constraints and ORDER BY terms into an `sqlite3_index_info`, recording hidden metadata beside it. `whereLoopAddVirtual()` first calls `xBestIndex()` with all constraints usable, then retries with LIMIT/OFFSET disabled when necessary, and finally explores subsets of usable prerequisite masks so plans with different join-order dependencies are represented. `whereLoopAddVirtualOne()` validates `argvIndex` continuity, rejects malformed `xBestIndex()` outputs, captures consumed constraints, handles IN-as-iterator requests, disables ORDER BY consumption when normal IN iteration makes ordering unsafe, transfers `idxStr` ownership into the candidate loop, and inserts the candidate into the loop list.

B-tree planning flows through `whereLoopAddBtree()`. For rowid tables, it prepends a fake integer-primary-key `Index` before real indexes. It may first add automatic-index candidates, then loops over each eligible real or fake index. Each index can contribute a full scan, a covering-index scan, a partial-index scan, or constrained searches. Covering status is determined from index metadata, column-use bitmasks, partial-index constants, and when needed a full SELECT expression walk. `whereLoopAddBtreeIndex()` recursively appends constraints one index column at a time, considering IN multipliers, STAT4 estimates, likelihood hints, range bounds, vector ranges, LIKE range pairs, unique-row flags, seek-scan decisions, and skip-scan expansion.

Candidate insertion is incremental and pruning-heavy. `whereLoopInsert()` enforces a planner search limit, adjusts costs against already-known subset/superset candidates, sends OR-subclause costs into a bounded `WhereOrSet` when requested, otherwise finds and replaces dominated list entries. It preserves ownership semantics for virtual-table strings and automatic-index `Index` objects by transferring those fields from the template into the stored `WhereLoop`.

Once candidates exist for every table, `wherePathSolver()` chooses a join path with bounded dynamic programming. It keeps only `mxChoice` paths per depth, where the cap is one for single-table queries, five for two-table joins, and normally twelve or eighteen for larger joins depending on the star-query heuristic. For each candidate extension, it checks prerequisites, avoids unprofitable automatic indexes for very low iteration counts, accumulates setup/run/output costs, optionally evaluates ORDER BY satisfaction, adds sorting or partial-sorting cost, and prunes against existing paths over the same loop mask. The winner is copied into `pWInfo->a[]`, including source table indices, cursors, row estimate, reverse scan mask, ORDER BY satisfaction count, DISTINCT status, and inner-loop ordering flags for ORDER BY LIMIT and min/max.

Ordering analysis is woven into path solving. `wherePathSatisfiesOrderBy()` marks ORDER BY terms satisfied by constants, equality constraints, one-row loops, index order, virtual-table `orderByConsumed`, subquery ORDER BY, unique non-null order-distinct columns, and GROUP BY/DISTINCT adjacency semantics. It also tracks reverse scan eligibility and null-ordering constraints. If a no-sort path is not found after the initial solver pass, `whereInterstageHeuristic()` can disable full-scan alternatives for tables that were first planned with equality searches before the second solver run.

`sqlite3WhereBegin()` is the entry point that prepares this machinery. In this chunk it checks incompatible flags, truncates unoptimizable ORDER BY/GROUP BY lists at the `Bitmask` width, rejects joins with more than `BMS` FROM terms, adjusts the table count for OR-subclauses, allocates `WhereInfo` plus the builder template loop in one block, initializes labels and masks, initializes the `WhereClause`, splits the input WHERE expression on AND, and begins the no-FROM branch by marking ORDER BY and DISTINCT as trivially satisfied.

## State And Persistence Behavior

- The planner mostly mutates in-memory compiler state. It does not write persistent database content in this chunk, but it can generate later bytecode that constructs ephemeral autoindexes and Bloom-filter blobs at statement runtime.
- `WhereInfo` owns the main planning state: parse context, FROM list, ORDER BY and result lists, SELECT pointer, `WhereClause`, mask set, selected `WhereLevel` array, all candidate `WhereLoop` objects, one-pass cursor fields, row estimates, labels, ordering/distinct flags, and memory blocks to free.
- `WhereLoop` objects are mutable candidates. Their fields encode table index, prerequisites, self mask, selected terms, B-tree or virtual-table details, estimated setup/run/output costs, sort-index id, skip-scan counts, range-bound counts, and behavior flags such as `WHERE_INDEXED`, `WHERE_IDX_ONLY`, `WHERE_AUTO_INDEX`, `WHERE_VIRTUALTABLE`, `WHERE_COLUMN_IN`, `WHERE_BLOOMFILTER`, `WHERE_ONEROW`, `WHERE_MULTI_OR`, and `WHERE_SELFCULL`.
- Candidate-list memory is owned by `WhereInfo` and cleaned by `whereInfoFree()`. Template loops transfer owned `idxStr` and autoindex `Index` storage into list entries through `whereLoopXfer()`.
- `HiddenIndexInfo` caches RHS values for virtual-table constraints. `freeIndexInfo()` releases these `sqlite3_value` objects and any `idxStr` not transferred to a loop.
- `constructAutomaticIndex()` allocates an internal `Index` object representing a transient covering index, stores it in `pLoop->u.btree.pIndex`, and emits bytecode to build it once using `OP_Once`, `OP_OpenAutoindex`, `OP_IdxInsert`, and optional `OP_FilterAdd`.
- Bloom filters are runtime blobs in VDBE registers. Planning marks `WHERE_BLOOMFILTER`; construction clears that flag and sets `WhereLevel.regFilter` to the register containing the filter.
- Partial-index and expression-index optimizations add `IndexedExpr` nodes to `Parse->pIdxEpr` or `Parse->pIdxPartExpr`. Cleanup is registered with `sqlite3ParserAddCleanup()` so these lists are released with the parse object.
- Table flags can be updated as planner feedback. For example, non-unique indexed planning and Bloom-filter consideration can set `TF_MaybeReanalyze`, signaling that better statistics may improve plan quality.
- `Parse->nQueryLoop` is consumed by solver cost seeding, and `sqlite3WhereBegin()` saves it in `WhereInfo.savedNQueryLoop` for later restoration outside this chunk.
- `WHERETRACE` debug state is read globally and can cause diagnostic printing; it does not change planning semantics except for debug-only fields such as loop ids and star-query deltas.

## Dependencies And Integration Points

- The file depends on `sqliteInt.h` and `whereInt.h` for SQLite core types, expression flags, `Where*` structs, VDBE opcodes, optimizer flags, bitmask macros, `LogEst`, and planner constants.
- It integrates tightly with expression analysis through `sqlite3ExprSkipCollateAndLikely()`, `sqlite3ExprCompareCollSeq()`, `sqlite3IndexAffinityOk()`, `sqlite3WhereExprUsage()`, expression walkers, implication checks, constant extraction, vector-size helpers, LIKE/GLOB detection, and indexed-expression comparison.
- It depends on schema objects `Table`, `Index`, `SrcList`, `SrcItem`, `Select`, `ExprList`, column affinity/collation metadata, row-estimate arrays, partial-index predicates, and STAT1/STAT4 fields.
- It emits and edits VDBE bytecode using APIs such as `sqlite3VdbeAddOp*()`, `sqlite3VdbeGoto()`, `sqlite3VdbeJumpHere()`, `sqlite3VdbeSetP4KeyInfo()`, `sqlite3GenerateIndexKey()`, `sqlite3ExprIfFalse()`, and scan-status helpers.
- It integrates with virtual tables via `sqlite3_index_info`, `xBestIndex()`, virtual-table error messages, all-schema use flags, and public helper interfaces callable from inside `xBestIndex()`.
- It integrates with optimizer feature switches including automatic indexes, Bloom filters, Bloom pulldown, skip-scan, seek-scan, STAT4, star-query handling, ORDER BY index joins, ORDER BY subquery optimization, omit-noop-join, distinct optimization, reverse scan order, and covering-index scans.
- Conditional compilation gates substantial behavior: `SQLITE_OMIT_AUTOMATIC_INDEX`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_ENABLE_STAT4`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_COSTMULT`, `SQLITE_DEBUG`, `WHERETRACE_ENABLED`, and `SQLITE_ALLOW_ROWID_IN_VIEW`.
- Join planning depends on parser join flags such as `JT_LEFT`, `JT_RIGHT`, `JT_LTORJ`, `JT_OUTER`, and `JT_CROSS`, plus expression properties `EP_OuterON` and `EP_InnerON`.
- Test and diagnostics integrate through `testcase()`, `NEVER()`, `ALWAYS()`, fault simulation, `WHERETRACE`, scanstatus `OP_Explain`, `sqlite3_log(SQLITE_WARNING_AUTOINDEX)`, and warning logs for abbreviated planner search.

## Risks And Edge Cases

- Planner bitmasks cap optimizable joins and ORDER BY terms. `sqlite3WhereBegin()` rejects more than `BMS` FROM terms and disables ORDER BY/DISTINCT optimization when ORDER BY has at least `BMS` terms.
- Transitive equality scanning must preserve affinity, collation, expression-index matching, and outer-join semantics. Returning an incompatible term can produce wrong results, while over-filtering can miss valid indexes.
- Outer joins and RIGHT/FULL join transformations are high-risk. The code carefully limits constraint use, OR optimization, partial-index use, automatic indexes, no-op join omission, and index-on-expression scans where null-row or join-side semantics could be violated.
- Virtual-table `xBestIndex()` outputs are trusted only after validation. Invalid `argvIndex`, gaps, duplicate argument indexes, unusable consumed constraints, or unsafe LIMIT/OFFSET plus IN combinations become errors or retries.
- IN planning has several delicate cases: vector IN terms must avoid double-counting multipliers, `x IN (SELECT ...)` is guessed as 25 rows, IN can invalidate virtual-table ordering, and seek-scan decisions use uncertain estimates.
- STAT4 improves selectivity but relies on extracting comparable probe values and loading collations. Failures must degrade safely to fallback estimates or propagate allocation/collation errors.
- Covering-index detection with expression indexes is intentionally conservative. A false negative only loses performance, but a false positive can produce incorrect bytecode or assertion failures.
- Automatic indexes are transient and covering by necessity. Missing a required output column, rowid, primary-key column, or coroutine copy rewrite would make later reads incorrect.
- Bloom-filter decisions are heuristic and depend on STAT1. Marking a loop as Bloom-filtered also clears `WHERE_IDX_ONLY`, because the table cursor must be available to populate or probe the filter.
- Cost adjustments are intentionally biased. Changes to constants such as full-scan penalty, skip-scan repeat threshold, autoindex setup cost, sort penalty, star-query path cap, or LIKE pattern reduction can shift many plans and cause performance regressions.
- The star-query heuristic mutates scan costs globally within the candidate list. Its constraints around outer/CROSS joins and self-joins are important to avoid helping one workload while regressing ordinary joins.
- `whereInterstageHeuristic()` deliberately disables some loops before the second solver pass. If applied too broadly it could prevent legitimate order-preserving plans; if too narrowly it can allow severe full-scan regressions.
- The line range ends before `sqlite3WhereBegin()` finishes. Later code in the same file is responsible for completing no-FROM handling, mask creation, full solver invocation, cursor opening, loop bytecode generation, error cleanup, and `sqlite3WhereEnd()`.

## Test Signals

- Query-plan tests should cover rowid equality, unique-index equality, non-unique equality, IS and IS NULL, IN-list, IN-subquery, vector IN, range scans, vector range scans, LIKE/GLOB range optimization, skip-scan, and seek-scan choices.
- Statistics tests should compare plans and estimates with no ANALYZE data, STAT1 only, and STAT4 enabled, including equality, IN-list, range, skip-scan range, low-selectivity terms, and `likelihood()` hints.
- Automatic-index tests should assert warning behavior, covering-column inclusion, partial automatic-index predicates, coroutine subquery handling, `OP_OpenAutoindex`/`OP_IdxInsert` generation, and behavior with `NOT INDEXED`, `INDEXED BY`, recursive CTEs, correlated subqueries, and RIGHT JOINs.
- Virtual-table tests should verify `xBestIndex()` receives expected constraints, collations, ORDER BY terms, distinct modes, usable flags, IN handling, RHS values, LIMIT/OFFSET retries, malformed callback output errors, and all-schema dependency behavior.
- ORDER BY/GROUP BY/DISTINCT tests should cover full satisfaction, block sorting, reverse index scans, NULLS FIRST/LAST, collation mismatches, ORDER BY LIMIT, min/max ordering, DISTINCT redundancy, DISTINCT ordered output, GROUP BY sortedness, and subquery ORDER BY propagation.
- Join-order tests should cover CROSS JOIN barriers, LEFT/RIGHT/FULL join constraints, EXISTS-to-JOIN dependencies, no-op LEFT JOIN omission, multi-index OR planning, and no OR optimization for RIGHT/FULL joins.
- Covering-index tests should include normal covering indexes, partial-index constant substitution, expression indexes, virtual columns, columns beyond the bitmask width, WITHOUT ROWID primary keys, and RIGHT JOIN index-on-expression exclusions.
- Bloom-filter tests should confirm marking only when STAT1 exists, searches exceed table size, self-culling equality loops are present, and optimizer flags can disable Bloom filters or Bloom pulldown.
- Star-schema regression tests should assert that dimension table full-scan costs are raised only for qualifying inner-join star queries and not for self-joins, CROSS joins, or outer-join-separated tables.
- Fast-path tests should verify `whereShortCut()` for single-table rowid and full unique-index lookups, and that it declines virtual tables, OR subclauses, `INDEXED BY`, `NOT INDEXED`, partial indexes, and incomplete unique keys.
- Error-path tests should cover OOM during `WhereInfo`, `WhereLoop`, `sqlite3_index_info`, autoindex, STAT4 probe, and indexed-expression allocations, plus planner search-limit warnings and the "no query solution" path.

### subset-b-008808: lines 6956-7886

# sources/storage-engines/sqlite/src/where.c lines 6956-7886

## Scope

This chunk covers the final 931 lines of `where.c`. It starts inside `sqlite3WhereBegin()` after the `WhereInfo`, `WhereClause`, and `WhereLoopBuilder` scaffolding has already been allocated and the WHERE expression has been split into terms. It continues through the rest of `sqlite3WhereBegin()`, the debug-only opcode rewrite trace helper, and the complete `sqlite3WhereEnd()` implementation.

The slice is the handoff point between query planning and VDBE bytecode generation. It assigns FROM-clause masks, analyzes WHERE terms, builds and solves candidate `WhereLoop` plans, opens table/index cursors, emits the start of each nested loop, then later emits loop termination code and post-generation rewrites that turn table reads into index reads when a covering index or expression-index plan permits it.

## Purpose

- Finish planning a SELECT, UPDATE, or DELETE scan after earlier setup has initialized the `WhereInfo` object.
- Translate analyzed WHERE terms, ORDER BY or GROUP BY requirements, DISTINCT requirements, LIMIT estimates, join constraints, and optimization flags into selected nested-loop `WhereLevel` entries.
- Generate VDBE opcodes that open all required table, index, virtual table, ephemeral RIGHT JOIN, automatic-index, and Bloom-filter cursors.
- Emit the bytecode prologue for each nested loop using `sqlite3WhereCodeOneLoopStart()`, leaving callers to generate the loop body between `sqlite3WhereBegin()` and `sqlite3WhereEnd()`.
- Generate the bytecode epilogue in `sqlite3WhereEnd()`, including `Next`/`Prev`/`VNext` instructions, IN-loop iteration, skip-scan continuation, LIKE range repetition, LEFT JOIN null-row fallback, RIGHT JOIN unmatched-row handling, and final break-label resolution.
- Perform late VDBE opcode rewriting so result-body code that initially reads from a table cursor can instead read from the selected index cursor when the plan is covering or potentially covering.
- Maintain query-planner bookkeeping such as `pParse->nQueryLoop`, `pWInfo->eOnePass`, `pWInfo->eDistinct`, `pWInfo->nOBSat`, cursor ids, labels, scan status, and debug/trace output.

## Important APIs, Types, And Functions

- `sqlite3WhereBegin(Parse*, SrcList*, Expr*, ExprList*, ExprList*, Select*, u16, int)` is the main entry point whose tail is covered here. It returns a populated `WhereInfo *` on success or `0` on allocation/planning/codegen error.
- `sqlite3WhereEnd(WhereInfo *pWInfo)` is the paired close-out API. Callers generate the SELECT/UPDATE/DELETE loop body after `sqlite3WhereBegin()` returns, then call this function to finish all nested loops and free `WhereInfo`.
- `WhereInfo` is the continuity object spanning begin/end. Fields used heavily in this chunk include `pParse`, `pTabList`, `pOrderBy`, `pResultSet`, `pSelect`, `aiCurOnePass`, `iBreak`, `iContinue`, `savedNQueryLoop`, `wctrlFlags`, `iLimit`, `nLevel`, `nOBSat`, `eOnePass`, `eDistinct`, `nRowOut`, `iTop`, `iEndWhere`, `pLoops`, `sWC`, `sMaskSet`, `revMask`, and `a[]`.
- `WhereLevel` describes the implementation state for one selected nested loop. This chunk fills or consumes `iFrom`, `iTabCur`, `iIdxCur`, `addrBrk`, `addrHalt`, `addrCont`, `addrFirst`, `addrBody`, `addrNxt`, `addrSkip`, `regBignull`, `addrBignull`, `iLeftJoin`, `pRJ`, `u.in`, `u.pCoveringIdx`, and the loop-ending opcode fields `op/p1/p2/p3/p5`.
- `WhereLoop` is the selected algorithm for a `WhereLevel`. This chunk consumes `wsFlags` and `u.btree.pIndex` to decide cursor opens, one-pass eligibility, index-only behavior, OR optimization behavior, DISTINCT skip-ahead, IN-loop cleanup, and covering-index rewrites.
- `WhereLoopBuilder sWLB` carries the candidate-loop builder state. This chunk calls `whereLoopAddAll(&sWLB)`, may discard and rebuild `pWInfo->pLoops` for the STAT4 second pass, and then calls `wherePathSolver()`.
- `WhereRightJoin` is allocated for RIGHT JOIN levels. It stores an ephemeral match cursor, a Bloom-filter register, a return register, and subroutine addresses used later by `sqlite3WhereRightJoinLoop()`.
- `createMask()`, `sqlite3WhereGetMask()`, and `WhereMaskSet` assign stable bitmasks to FROM cursors. The ordering invariant is important for LEFT and RIGHT join dependency tests elsewhere in the planner.
- `sqlite3WhereTabFuncArgs()` adds hidden function-argument constraints for table-valued functions before expression analysis.
- `sqlite3WhereExprAnalyze()` annotates `WhereTerm` objects with operator classes, prerequisite masks, virtual terms, and other planner metadata. `sqlite3WhereAddLimit()` adds LIMIT-derived planner information when applicable.
- `sqlite3ExprIfFalse()` emits an early bypass jump for constant-relative false WHERE terms. It targets `pWInfo->iBreak` and marks the term `TERM_CODED`.
- `isDistinctRedundant()`, `wherePathSatisfiesOrderBy()`, `whereInterstageHeuristic()`, and `wherePathSolver()` determine DISTINCT and ordering modes and choose a lowest-cost loop path.
- `whereShortCut()` can bypass the full loop-building solver for a simple single-table case.
- `whereOmitNoopJoin()` can delete join levels that do not affect the result when join and DISTINCT semantics allow it.
- `whereCheckIfBloomFilterIsUseful()` marks selected search loops that should use a Bloom filter before code generation.
- `sqlite3OpenTable()`, `sqlite3VdbeAddOp*()`, `sqlite3VdbeChangeP4()`, `sqlite3VdbeChangeP5()`, `sqlite3VdbeSetP4KeyInfo()`, `sqlite3TableLock()`, and `sqlite3CodeVerifySchema()` are the main codegen and schema-validation APIs used to open cursors.
- `whereAddIndexedExpr()` and `wherePartIdxExpr()` install expression-index and partial-index metadata for later code generation when a new index cursor is opened.
- `constructAutomaticIndex()` and `sqlite3ConstructBloomFilter()` emit transient access structures just before the corresponding loop begins.
- `sqlite3WhereExplainOneScan()`, `sqlite3WhereAddScanStatus()`, and `sqlite3WhereAddExplainText()` maintain EXPLAIN QUERY PLAN and scan-status instrumentation.
- `sqlite3WhereCodeOneLoopStart()` emits the body-entry code for one nested scan and updates `WhereLevel` fields that `sqlite3WhereEnd()` later relies on.
- `translateColumnToCopy()` rewrites coroutine table reads to register copies in `sqlite3WhereEnd()`.
- `sqlite3TableColumnToIndex()`, `sqlite3StorageColumnToTable()`, and `sqlite3PrimaryKeyIndex()` map table column numbers to index column numbers for covering-index opcode rewriting.
- `OpcodeRewriteTrace()` is a macro. In non-debug builds it is a no-op; in debug builds it maps to `sqlite3WhereOpcodeRewriteTrace()`, which prints rewritten VDBE opcodes when `SQLITE_VdbeAddopTrace` is active.

## Control Flow

The chunk begins with the no-FROM case emitting an EXPLAIN QUERY PLAN row for a constant-row scan. For real FROM clauses, it assigns a bitmask to every `SrcItem` cursor in the full `pTabList`, even if `WHERE_OR_SUBCLAUSE` means only the first source is being coded. It also calls `sqlite3WhereTabFuncArgs()` for each source, allowing table-valued-function arguments to become WHERE-clause constraints.

After mask creation, `sqlite3WhereExprAnalyze()` analyzes all split terms and `sqlite3WhereAddLimit()` may inject LIMIT information. The false-WHERE-term bypass optimization then scans base WHERE terms for non-virtual terms with no local table prerequisites. If such a term is safe with respect to ON-clause and outer-join semantics, and is deterministic for a non-empty FROM clause, bytecode is emitted to jump directly to `pWInfo->iBreak` when the term is false or NULL. This avoids generating rows for impossible predicates while preserving legacy behavior for nondeterministic functions.

DISTINCT handling is normalized next. If `SQLITE_DistinctOpt` is disabled, the DISTINCT-specific flag is cleared. If DISTINCT is provably redundant, `pWInfo->eDistinct` becomes `WHERE_DISTINCT_UNIQUE`. Otherwise, if there is no caller-supplied ORDER BY, the planner treats the result set as an ordering target using `WHERE_DISTINCTBY` so duplicates can become adjacent.

Planner tracing can print the select tree and WHERE terms. The main planner path then either uses `whereShortCut()` for a qualifying one-table query or calls `whereLoopAddAll()` to build candidate loops for all FROM terms. Under `SQLITE_ENABLE_STAT4`, a builder flag can request a second full pass if STAT4-derived truth probabilities changed while later loops were being computed; the old `WhereLoop` list is deleted and rebuilt before solving.

`wherePathSolver(pWInfo, 0)` selects the initial loop order and access methods. If ordering is relevant, `whereInterstageHeuristic()` can adjust state between solver passes, then `wherePathSolver()` runs again with an output-row estimate. For DISTINCT queries, the selected row estimate is tuned down by `30` LogEst units, matching an assumed factor of eight reduction. If there is no ORDER BY and the connection has `SQLITE_ReverseOrder`, `whereReverseScanOrder()` reverses eligible scan directions.

After a solution is selected, optional optimizer passes run before cursor opening. `whereOmitNoopJoin()` can shrink `pWInfo->nLevel` and `nTabList` for joins whose tables do not affect the result. `whereCheckIfBloomFilterIsUseful()` can mark search loops for Bloom-filter construction. Tracing then prints the final WHERE clause and solution, and `pParse->nQueryLoop` is incremented by the estimated output rows.

For one-pass UPDATE/DELETE callers, the code checks that the selected single-level plan is either one-row or a safe multi-row plan. Multi-row one-pass requires `WHERE_ONEPASS_MULTIROW`, a non-virtual table, no OR optimization unless duplicates are acceptable, and the `SQLITE_OnePass` optimization. If a rowid table plan was index-only, index-only is cleared so the writable table cursor is opened and `OPFLAG_FORDELETE` can be set for multi-row delete.

The cursor-opening loop iterates over selected `WhereLevel` entries. It chooses `addrHalt` based on outer-loop and join state, opens virtual table cursors with `OP_VOpen`, opens ordinary tables with `sqlite3OpenTable()` unless an index-only plan can avoid them, and still opens tables for RIGHT JOIN and LEFT-of-RIGHT-JOIN cases where null-row or unmatched-row handling needs table state. For table opens, it can reduce the column count in the open opcode P4 operand based on `colUsed`, set cursor hints and `OPFLAG_FORDELETE`, emit `OP_ColumnsUsed`, and add an `OP_IfEmpty` early-exit for some deeper inner tables.

If the selected loop uses an index, the code chooses the index cursor. WITHOUT ROWID primary-key OR subclauses reuse the table cursor. One-pass uses the caller-provided auxiliary cursor range. OR subclauses may reopen the caller-provided index cursor. Otherwise a new cursor number is allocated and expression-index or partial-index metadata is registered. When an actual open opcode is needed, `OP_OpenRead`, `OP_OpenWrite`, or `OP_ReopenIdx` is emitted with key info, optional `OPFLAG_SEEKEQ`, comments, and optional index column-used masks.

RIGHT JOIN setup allocates a `WhereRightJoin` object, reserves an ephemeral match cursor, creates a Bloom filter blob register, initializes the return register, and opens an ephemeral btree keyed by rowid or by the WITHOUT ROWID primary key. It then clears `WHERE_IDX_ONLY` for the loop and disables ORDER BY/GROUP BY and ordered DISTINCT satisfaction because RIGHT JOIN unmatched-row output disrupts ordering.

After all opens, `pWInfo->iTop` records the VDBE address at the top of WHERE execution. The second `sqlite3WhereBegin()` loop emits actual loop starts. Materialized subqueries are populated once for non-correlated sources or every time for correlated sources. Automatic indexes and Bloom filters are constructed just before the scan that consumes them. EXPLAIN QUERY PLAN text is emitted, `addrBody` is recorded, `sqlite3WhereCodeOneLoopStart()` emits the start of the scan, and scan-status instrumentation is added for ordinary non-OR loops. `pWInfo->iEndWhere` is saved immediately before returning `pWInfo`.

If any error or allocation failure occurs after `pWInfo` allocation, control jumps to `whereBeginError`, restores `pParse->nQueryLoop`, frees `WhereInfo` with `whereInfoFree()`, touches debug-only routines to avoid compiler warnings, and returns `0`.

`sqlite3WhereEnd()` starts by recording the current VDBE address as `iEnd`, then iterates `WhereLevel` entries from inner to outer. RIGHT JOIN levels first close the interior subroutine by resolving the old continue label, replacing it with a dummy label, saving the subroutine end address, and emitting `OP_Return`. DISTINCT ordered scans may emit a skip-ahead seek (`OP_SeekLT` or `OP_SeekGT`) for the innermost indexed loop when statistics show enough duplicates. EXISTS-to-JOIN converted sources emit a break jump after one successful row.

The loop terminator then resolves `addrCont`, emits the level's ending opcode if it is not `OP_Noop`, resolves bignull and DISTINCT skip-ahead labels, and closes any nested IN loops in reverse order. IN-loop cleanup retargets null checks, optionally emits `OP_IfNotOpen` for LEFT JOIN cases whose IN cursor may not have opened, and can emit `OP_IfNoHope` for early-out index probes before adding `OP_Next` or `OP_Prev` for the IN cursor.

After `addrBrk` is resolved, RIGHT JOIN subroutine bodies return to the stored return register. Skip-scan and LIKE range repetition labels are wired up. LEFT JOIN levels then check their match flag; if no row matched, table and index cursors are moved to null rows, coroutine result registers may be nulled, and control jumps or gosubs back to the loop body so the caller body runs once with NULL right-side values.

The second `sqlite3WhereEnd()` pass iterates outer to inner for post-body rewrites. RIGHT JOIN levels delegate unmatched-row generation to `sqlite3WhereRightJoinLoop()` and skip normal rewriting. Coroutine subqueries call `translateColumnToCopy()` to turn table-column reads into register copies. Indexed loops select either `pLoop->u.btree.pIndex` or `pLevel->u.pCoveringIdx` for multi-index OR. If an index exists and no malloc failure has occurred, the code scans VDBE opcodes from just after the loop body marker to either `iEnd` or `pWInfo->iEndWhere` for one-pass rowid tables.

During rewrite, expression-index cache entries for this index cursor are disabled because the code is about to rewrite direct table references. `OP_Column` and optional `OP_Offset` against the table cursor are mapped through storage-column and index-column mappings. If the column is present in the index, the opcode cursor and column number are changed to use `iIdxCur`. If a covering-index plan cannot satisfy a referenced column, an internal planner error is reported. If the weaker `WHERE_EXPRIDX` flag was optimistic, it is cleared and EXPLAIN text is rewritten. `OP_Rowid` becomes `OP_IdxRowid`, and `OP_IfNullRow` is retargeted to the index cursor.

Finally, `sqlite3WhereEnd()` resolves the global break label, restores `pParse->nQueryLoop`, frees `WhereInfo`, subtracts the number of RIGHT JOIN subroutines from `pParse->withinRJSubrtn`, and returns.

## State And Persistence Behavior

- The central persistent-in-call state is `WhereInfo`, allocated by `sqlite3WhereBegin()` and freed by `sqlite3WhereEnd()` or the begin-error path.
- `pWInfo->sMaskSet` stores cursor-to-bitmask assignments. The assignments are transient but determine join-order legality, ON-clause applicability, and outer-join dependency handling throughout planning and code generation.
- `pWInfo->sWC` stores analyzed `WhereTerm` state. This chunk mutates term flags such as `TERM_CODED` when a false-term bypass is emitted.
- `pWInfo->pLoops` owns the candidate `WhereLoop` list. In the STAT4 second-pass case, all old loop objects are explicitly deleted and regenerated before solving.
- `pWInfo->a[]` stores selected `WhereLevel` implementation state. This chunk fills cursor ids, labels, selected loop pointers, right-join metadata, loop-ending opcodes, IN-loop metadata, and body addresses consumed later by `sqlite3WhereEnd()`.
- `pParse->nQueryLoop` is saved before this chunk by the earlier `WhereInfo` setup, incremented by selected row estimates during planning, and restored in both normal `sqlite3WhereEnd()` cleanup and `whereBeginError`.
- `pParse->nTab` is incremented for new index cursors, RIGHT JOIN match cursors, and other generated cursors. Those cursor numbers persist in the generated VDBE program, not in database storage.
- `pParse->nMem` is incremented for RIGHT JOIN Bloom and return registers and for DISTINCT skip-ahead register ranges in `sqlite3WhereEnd()`.
- `pWInfo->aiCurOnePass[]` records writable table and index cursors for one-pass UPDATE/DELETE callers. This is an observable contract through `sqlite3WhereOkOnePass()` outside this chunk.
- VDBE bytecode is appended to `pParse->pVdbe`. The generated opcodes are persistent within the prepared statement until the statement is finalized, but this chunk does not write database content by itself.
- Schema-read verification is recorded with `sqlite3CodeVerifySchema()` for every opened table/index database. This ties the prepared statement to schema-cookie validation at execution time.
- RIGHT JOIN setup creates ephemeral runtime structures and a blob-backed Bloom filter in registers. These structures live for statement execution and are not stored in database files.
- Covering-index rewrites mutate already-emitted VDBE opcodes between `sqlite3WhereBegin()` and `sqlite3WhereEnd()`. This late mutation is deliberate: caller-generated loop-body code initially references table cursors without needing to know whether the table will be omitted.
- Debug and scan-status state is conditional. With `WHERETRACE_ENABLED`, trace output reads global `sqlite3WhereTrace`; with `SQLITE_ENABLE_STMT_SCANSTATUS`, scan status opcodes and addresses become visible to statement scan-status APIs.

## Dependencies And Integration Points

- The chunk depends on planner internals from earlier `where.c` sections: WHERE-term analysis, loop enumeration, OR-loop handling, automatic-index planning, Bloom-filter planning, path solving, join omission, reverse scan order, and loop-start code generation.
- It depends on internal definitions in `whereInt.h`, especially `WhereInfo`, `WhereLevel`, `WhereLoop`, `WhereLoopBuilder`, `WhereRightJoin`, `WhereClause`, `WhereTerm`, and the `WHERE_*` loop flags such as `WHERE_IDX_ONLY`, `WHERE_INDEXED`, `WHERE_VIRTUALTABLE`, `WHERE_MULTI_OR`, `WHERE_AUTO_INDEX`, `WHERE_BLOOMFILTER`, `WHERE_IN_ABLE`, `WHERE_ONEROW`, `WHERE_SKIPSCAN`, `WHERE_EXPRIDX`, `WHERE_BIGNULL_SORT`, and `WHERE_IN_SEEKSCAN`.
- It depends on public-ish planner control flags from `sqliteInt.h`, including `WHERE_WANT_DISTINCT`, `WHERE_DISTINCTBY`, `WHERE_GROUPBY`, `WHERE_AGG_DISTINCT`, `WHERE_KEEP_ALL_JOINS`, `WHERE_OR_SUBCLAUSE`, `WHERE_ONEPASS_DESIRED`, `WHERE_ONEPASS_MULTIROW`, `WHERE_DUPLICATES_OK`, `WHERE_ORDERBY_MIN`, and `WHERE_USE_LIMIT`.
- It integrates with SELECT code generation through the begin/end contract: `sqlite3WhereBegin()` opens cursors and positions rows, caller code emits result/update/delete logic, and `sqlite3WhereEnd()` closes the loop structure and rewrites body opcodes.
- It integrates with UPDATE and DELETE through one-pass state. Callers that request one-pass inspect `pWInfo->eOnePass` and `aiCurOnePass[]` to decide whether rowids must be collected first or whether the table can be modified in place.
- It integrates with virtual tables by emitting `OP_VOpen` for loops marked `WHERE_VIRTUALTABLE` and by avoiding ordinary table open behavior for virtual sources that are not selected as virtual-table loops.
- It integrates with table-valued functions through `sqlite3WhereTabFuncArgs()`, which makes function arguments participate in WHERE analysis before loops are built.
- It integrates with the VDBE opcode layer broadly: cursor opens, labels, jumps, null-row handling, IN-loop iteration, rowid/index-rowid reads, ephemeral btrees, subroutines, and key-info P4 payloads all use VDBE APIs.
- It integrates with schema management through `sqlite3SchemaToIndex()`, `sqlite3CodeVerifySchema()`, `sqlite3TableLock()`, and btree table/index root page numbers.
- It integrates with optional compile-time features: `SQLITE_ENABLE_STAT4`, `SQLITE_ENABLE_CURSOR_HINTS`, `SQLITE_ENABLE_COLUMN_USED_MASK`, `SQLITE_ENABLE_OFFSET_SQL_FUNC`, `SQLITE_DISABLE_SKIPAHEAD_DISTINCT`, `SQLITE_LIKE_DOESNT_MATCH_BLOBS`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_OMIT_AUTOMATIC_INDEX`, `SQLITE_DEBUG`, and `WHERETRACE_ENABLED`.
- It integrates with RIGHT JOIN support through `JT_RIGHT`, `JT_LTORJ`, `WhereRightJoin`, `sqlite3WhereRightJoinLoop()`, and `pParse->withinRJSubrtn`.
- It integrates with ORDER BY, GROUP BY, and DISTINCT satisfaction by updating `pWInfo->nOBSat`, `revMask`, and `eDistinct`, and by disabling those optimizations when RIGHT JOIN makes the produced order unreliable.
- It integrates with EXPLAIN and statement scan status through `ExplainQueryPlan`, `sqlite3WhereExplainOneScan()`, `sqlite3WhereAddExplainText()`, `VdbeComment()`, `VdbeModuleComment()`, and `sqlite3WhereAddScanStatus()`.

## Risks And Edge Cases

- The false-WHERE-term bypass is semantically delicate. It must not move nondeterministic functions out of per-row evaluation in FROM queries, and it must respect ON-clause behavior for LEFT, RIGHT, and FULL joins.
- Mask assignment intentionally uses the full `pTabList->nSrc`, not only `nTabList`, because OR subclause planning may code one table while still needing stable masks for all FROM terms. A change here could break join prerequisite reasoning.
- The STAT4 second pass deletes and rebuilds all candidate loops. Any new loop-owned allocation must be freed correctly by `whereLoopDelete()` or the second-pass path can leak memory or reuse stale estimates.
- One-pass UPDATE/DELETE is constrained by OR optimization, virtual tables, and covering-index behavior. Marking `ONEPASS_MULTI` too aggressively can corrupt update/delete semantics, while clearing `WHERE_IDX_ONLY` too late can leave no writable table cursor.
- RIGHT JOIN processing intentionally clears index-only mode and disables ordering optimizations. Re-enabling covering behavior or ORDER BY elimination for RIGHT JOIN without matching unmatched-row logic can produce wrong rows or wrong ordering.
- The table-open elision for index-only scans is balanced by late opcode rewriting. If `sqlite3WhereEnd()` misses a table cursor reference, the VDBE may read from an unopened cursor. If it rewrites too much, it can read the wrong column from an index.
- Expression-index covering detection is intentionally optimistic under `WHERE_EXPRIDX`. The fallback path clears the flag and rewrites EXPLAIN text, but true `WHERE_IDX_ONLY` failures are internal planner errors.
- Column-number mapping differs for rowid tables, WITHOUT ROWID tables, generated columns, storage columns, and `OP_Offset`. The rewrite path must preserve all of these mappings.
- `pLastOp = pOp + (last - k)` assumes the VDBE address range is valid and that the first instruction of the loop body is not a table read. Debug assertions check part of this, but release builds depend on the surrounding codegen contract.
- LEFT JOIN null-row fallback has special coroutine and multi-OR index handling. Missing a cursor/register nulling case can emit non-NULL values for unmatched outer-join rows.
- IN-loop cleanup contains several label retargeting operations around `OP_IsNull`, `OP_Affinity`, and `OP_IfNoHope`. Small ordering changes can cause NULL handling or early-out probes to skip required affinity or loop steps.
- The DISTINCT skip-ahead optimization depends on statistics (`hasStat1`, `aiRowLogEst`) and applies only to the innermost indexed loop. Broader application could skip valid rows.
- `OP_IfEmpty` early exit is only emitted for selected inner levels with compatible join state. Applying it across LEFT or LEFT-of-RIGHT join boundaries would suppress required NULL-extended rows.
- Compile-time feature guards split behavior significantly. Builds without automatic indexes, virtual tables, cursor hints, column-used masks, offset SQL functions, or skip-ahead DISTINCT need separate coverage because opcode sequences differ.
- Error paths rely on `db->mallocFailed`, `pParse->nErr`, and explicit `rc` checks. Any helper that records an error without these signals may allow code generation to continue with partially initialized planner state.

## Test Signals

- Basic SELECT tests should confirm that no-FROM queries produce a constant-row plan and that ordinary FROM queries open the expected table or covering-index cursors under `EXPLAIN` and `EXPLAIN QUERY PLAN`.
- WHERE constant-false tests should cover deterministic false predicates, outer-query references, nondeterministic functions such as `random()`, scalar subqueries with nondeterminism, and ON-clause predicates under LEFT, RIGHT, and FULL join forms.
- DISTINCT and ORDER BY tests should cover redundant DISTINCT, DISTINCT-by-result-set ordering, ordered DISTINCT skip-ahead, reverse scan order, and RIGHT JOIN cases where ordering satisfaction is deliberately disabled.
- STAT4-enabled builds should exercise queries whose term truth probabilities change after STAT4 probing, verifying that the second loop-building pass changes estimates without leaking or crashing.
- One-pass UPDATE and DELETE tests should cover one-row rowid updates, multi-row one-pass deletes, OR-optimized scans with and without duplicates allowed, virtual tables, rowid versus WITHOUT ROWID tables, and index-only plans that must reopen the table for writing.
- Cursor-opening tests should inspect VDBE bytecode for `OP_OpenRead`, `OP_OpenWrite`, `OP_ReopenIdx`, `OP_VOpen`, `OP_OpenEphemeral`, `OP_ColumnsUsed`, `OP_IfEmpty`, and `OPFLAG_SEEKEQ` across rowid, WITHOUT ROWID, virtual, partial-index, expression-index, and OR-subclause plans.
- RIGHT JOIN tests should assert that matched rows are tracked, unmatched right-side rows are emitted with left-side NULLs, ordering optimizations are not incorrectly reported as satisfied, and rowid and WITHOUT ROWID match keys both work.
- Bloom-filter and automatic-index tests should verify that marked loops emit `sqlite3ConstructBloomFilter()` or `constructAutomaticIndex()` before `sqlite3WhereCodeOneLoopStart()` and that malloc failures in those paths abort cleanly.
- LEFT JOIN tests should cover null-row fallback for table scans, index scans, multi-OR covering indexes, and coroutine subqueries.
- IN operator tests should include multi-column IN, NULL left operands, LEFT JOIN cases where an IN cursor is not opened, virtual-table exclusions from `OP_IfNoHope`, and early-out behavior under `WHERE_IN_EARLYOUT`.
- Skip-scan, bignull sort, and LIKE range tests should inspect generated loop-tail bytecode for correct label wiring and repeat counters.
- Covering-index tests should execute queries whose result body reads only indexed columns and confirm table cursors are not opened or table opcodes are rewritten to index opcodes. Negative tests should cover expression-index plans that look covering in EQP text but later prove non-covering.
- WITHOUT ROWID tests should verify primary-key column mapping during covering-index rewrite and OR-subclause primary-key cursor reuse.
- Debug builds should exercise `PRAGMA vdbe_addoptrace=on` or equivalent trace paths so `OpcodeRewriteTrace()` output is covered without changing release behavior.
- Scan-status-enabled tests should verify that `sqlite3WhereAddScanStatus()` is omitted for OR-subclauses and multi-OR loops but present for ordinary loops.
- Failure-injection tests should simulate allocation failures around loop rebuilding, cursor opens, RIGHT JOIN allocation, key-info allocation, automatic index/Bloom construction, and opcode rewriting, then confirm `pParse->nQueryLoop` is restored and `WhereInfo` memory is freed.
