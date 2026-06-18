# Research: sources/storage-engines/sqlite/src/select.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008784`: lines 1-7153, `Docs/researches/chunks/subset-b-008784_research.md`
- `subset-b-008785`: lines 7154-8967, `Docs/researches/chunks/subset-b-008785_research.md`

## Chunk Research

### subset-b-008784: lines 1-7153

# sources/storage-engines/sqlite/src/select.c lines 1-7153

## Scope

This chunk covers the front and middle of SQLite's SELECT implementation. It starts with `Select` ownership helpers and result-destination initialization, then moves through join normalization, DISTINCT and sorter bytecode generation, compound SELECT and recursive CTE execution, subquery flattening and push-down optimizations, FROM-clause expansion, CTE resolution, result metadata, and the first aggregate code-generation helpers. The chunk ends at line 7153 in the opening validation portion of `countOfViewOptimization()`, so that optimization is only partially covered here.

## Purpose

- Own, initialize, duplicate-sensitive-clean, and delete `Select` trees and their attached expression/source/window/WITH substructures.
- Convert parser-level SELECT syntax into structures ready for VDBE generation: assign cursors, resolve FROM terms, expand views/subqueries/CTEs, rewrite NATURAL/USING/ON joins, and expand `*`.
- Emit row-output bytecode for all SELECT destinations, including client output, scalar subqueries, EXISTS, IN-set materialization, UPDATE-FROM, coroutines, recursive-CTE queues, and ephemeral tables.
- Implement DISTINCT, ORDER BY, GROUP BY sorting, LIMIT/OFFSET counters, sorter-reference/deferred-row-load optimizations, and result-column metadata.
- Implement compound SELECT execution, including fast `VALUES`, recursive CTE queues, plain `UNION ALL`, and merge-based UNION/EXCEPT/INTERSECT/ordered compounds.
- Rewrite query trees for subquery flattening, predicate pushdown, constant propagation, HAVING-to-WHERE movement, unused subquery-column pruning, min/max and count optimizations, and compound ORDER BY collation compatibility.
- Prepare aggregate execution by allocating accumulator registers, opening ephemeral tables for DISTINCT and aggregate-local ORDER BY, updating accumulators, and finalizing aggregate functions.

## Important APIs, Types, And Functions

- `DistinctCtx` records whether DISTINCT is active, which `WHERE_DISTINCT_*` strategy was selected, and the ephemeral cursor/open-op address used by `codeDistinct()` and `fixDistinctOpenEph()`.
- `SortCtx` carries ORDER BY/GROUP BY sorter state: ORDER list, satisfied key prefix count, sorter cursor, return labels, temp-table open address, LIMIT optimization label, sorter flags, optional sorter-reference deferred cursors, deferred row-load state, and scanstatus instruction ranges.
- `RowLoadInfo` describes how `innerLoopLoadRow()` should populate result registers, including expression-code flags and optional extra primary-key expressions for sorter references.
- `sqlite3SelectNew()`, `sqlite3SelectDelete()`, `clearSelect()`, `findRightmost()`, and `sqlite3SelectDestInit()` are the basic SELECT AST and output-destination lifecycle helpers.
- `sqlite3JoinType()` parses accepted standard and legacy join-keyword combinations into `JT_*` bitmasks, reporting malformed combinations but returning an inner join fallback.
- `sqlite3ProcessJoin()`, `sqlite3SetJoinExpr()`, and `unsetJoinExpr()` convert NATURAL/USING/ON clauses into WHERE terms marked with `EP_OuterON` or `EP_InnerON` and join-cursor metadata.
- `codeDistinct()` and `fixDistinctOpenEph()` implement DISTINCT with either an ephemeral index, prior-row comparison for ordered data, or no-op handling when uniqueness is already proven.
- `selectInnerLoop()` is the central row-disposal routine. It evaluates result expressions or reads a source cursor, applies DISTINCT/OFFSET, pushes rows into sorters, or writes/yields/inserts according to `SelectDest.eDest`.
- `pushOntoSorter()`, `makeSorterRecord()`, `generateSortTail()`, and optional `selectExprDefer()` implement sorter record construction, ORDER BY LIMIT pruning, partially satisfied ORDER BY prefixes, sorter-reference row reloads, and final sorted output.
- `sqlite3KeyInfoAlloc()`, `sqlite3KeyInfoRef()`, `sqlite3KeyInfoUnref()`, and `sqlite3KeyInfoFromExprList()` allocate/refcount comparison metadata for sorters, DISTINCT indexes, compound merge comparison, and aggregate ephemeral tables.
- `sqlite3GenerateColumnNames()`, `columnTypeImpl()`, `generateColumnTypes()`, `sqlite3ColumnsFromExprList()`, `sqlite3SubqueryColumnTypes()`, and `sqlite3ResultSetOfSelect()` derive public column names, declaration types, origin metadata, affinities, collations, and transient result-set `Table` objects.
- `computeLimitRegisters()` creates and initializes VDBE registers for LIMIT, OFFSET, and LIMIT+OFFSET counters.
- `generateWithRecursiveQuery()` executes recursive CTEs using Current, Queue, and optional Distinct ephemeral tables.
- `multiSelect()`, `multiSelectValues()`, `generateOutputSubroutine()`, and `multiSelectByMerge()` handle compound SELECTs, including coroutine-based merge logic for UNION, UNION ALL, EXCEPT, INTERSECT, and ORDER BY compounds.
- `SubstContext`, `substExpr()`, `substSelect()`, `recomputeColumnsUsed()`, `renumberCursors()`, and related walkers support subquery flattening by replacing references to a subquery result cursor with copies of the underlying expressions and by remapping cursor numbers safely.
- `flattenSubquery()` is the main query flattener. It enforces SQLite's long list of semantic restrictions, handles compound UNION ALL flattening, moves FROM terms upward, transfers WHERE/ORDER/LIMIT state, and substitutes result expressions into the parent.
- `WhereConst`, `findConstInWhere()`, `propagateConstants()`, and rewrite walkers implement constant propagation through eligible `COLUMN=CONSTANT` top-level WHERE terms while preserving affinity/collation correctness.
- `pushDownWhereTerms()` duplicates safe outer WHERE terms into subqueries, including aggregate-to-HAVING handling and window-function partition checks.
- `disableUnusedSubqueryResultColumns()`, `minMaxQuery()`, `isSimpleCount()`, `havingToWhere()`, and `isSelfJoinView()` are targeted optimizers for unused projected columns, min/max ordering, simple `count(*)`, GROUP BY/HAVING filtering, and self-joined views.
- `sqlite3IndexedByLookup()` resolves `INDEXED BY` names on FROM terms.
- `convertCompoundSelectToSubquery()` rewrites compound SELECTs with ORDER BY COLLATE into a wrapper query when merge ordering cannot safely use different collations.
- `searchWith()`, `sqlite3WithPush()`, `resolveFromTermToCte()`, and `sqlite3SelectPopWith()` manage WITH-clause scope, CTE matching, recursive CTE marking, materialization-use bookkeeping, and column-list validation.
- `sqlite3ExpandSubquery()`, `selectExpander()`, `sqlite3SelectExpand()`, `selectAddSubqueryTypeInfo()`, `sqlite3SelectAddTypeInfo()`, and `sqlite3SelectPrep()` form the preparation pipeline before SELECT code generation.
- `analyzeAggFuncArgs()`, `optimizeAggregateUseOfIndexedExpr()`, `aggregateConvertIndexedExprRefToColumn()`, `assignAggregateRegisters()`, `resetAccumulator()`, `updateAccumulator()`, `finalizeAggFunctions()`, `explainSimpleCount()`, and `agginfoFree()` cover the first aggregate-analysis/codegen helpers in this chunk.

## Control Flow

SELECT construction begins with parser-created `Select` objects. `sqlite3SelectNew()` fills default result lists, source lists, flags, LIMIT pointers, WITH/window fields, and a unique `selId`. `clearSelect()` walks compound chains through `pPrior`, freeing expression lists, source lists, WHERE/GROUP/HAVING/ORDER/LIMIT expressions, WITH objects, and window lists. Most later routines assume these ownership rules when temporarily detaching subtrees for flattening or compound execution.

Preparation is centered on `sqlite3SelectPrep()`. It calls `sqlite3SelectExpand()` first, then `sqlite3ResolveSelectNames()`, then `sqlite3SelectAddTypeInfo()`. Expansion walks the SELECT tree. `selectExpander()` pushes active WITH scopes, assigns FROM-clause cursors, resolves subqueries, CTEs, tables, views, and virtual tables, resolves `INDEXED BY`, calls `sqlite3ProcessJoin()`, and expands wildcard result expressions. Name resolution happens only after this because wildcard expansion and view/subquery expansion must produce the expressions that names will bind to. Type information for ephemeral subquery tables is filled after name resolution because expression types and collations are not reliable earlier.

Join processing rewrites surface syntax into WHERE constraints. `sqlite3ProcessJoin()` synthesizes USING lists for NATURAL joins, validates USING columns on both sides, emits equality expressions for USING terms, and appends ON expressions into `Select.pWhere`. For outer joins, expressions are tagged with `EP_OuterON` and the right-side cursor so the WHERE planner/code generator can defer terms until after NULL-row generation. RIGHT/FULL joins receive additional handling: USING columns on the left may become `coalesce()` over multiple prior tables, ambiguous references are rejected, and left-side columns may be marked nullable.

The row-production path uses `selectInnerLoop()`. It allocates or reuses output registers, evaluates expressions unless reading from an existing result table, handles sorter-reference/deferred-row-load cases, applies DISTINCT, and dispatches by `SelectDest`. Direct destinations emit `OP_ResultRow`, `OP_Yield`, `OP_Insert`, `OP_IdxInsert`, `OP_FilterAdd`, or scalar-memory copies. Sorter destinations call `pushOntoSorter()` instead, then `generateSortTail()` later drains the sorter and writes to the real destination.

DISTINCT has three paths. For unordered or no-op strategies, `codeDistinct()` uses an ephemeral index with `OP_Found`, `OP_MakeRecord`, and `OP_IdxInsert`. For ordered rows, it compares the current result registers with a saved previous-row register range using `OP_Ne`/`OP_Eq` and `SQLITE_NULLEQ`. For proven-unique rows it emits no row tests. `fixDistinctOpenEph()` patches the earlier ephemeral-open opcode to a no-op, or to an `OP_Null` that initializes prior-row registers for ordered DISTINCT.

ORDER BY and GROUP BY sorting is split between push and tail phases. `pushOntoSorter()` builds sort keys, optional sequence numbers, result payloads, and LIMIT+OFFSET bounded sorters. If a prefix of ORDER BY is already satisfied by an index, it detects key changes, flushes the previous block through a subroutine, and resets the sorter. `generateSortTail()` opens pseudo cursors when needed, runs `OP_SorterSort` or `OP_Sort`, applies OFFSET for non-sorter ephemeral indexes, reloads deferred table rows for sorter references, reconstructs output columns, and dispatches them to the final destination.

Compound SELECTs go through `multiSelect()`. Fast `VALUES` compounds are emitted without recursive compound-depth enforcement by `multiSelectValues()`. Recursive CTEs are handled by `generateWithRecursiveQuery()`: the setup term fills a Queue, each queued row is copied into a Current pseudo-table, output is produced with LIMIT/OFFSET checks, and recursive terms refill the Queue until empty. `UNION ALL` without ORDER BY runs the left arm then the right arm, sharing LIMIT/OFFSET registers. Other compounds, or any compound with ORDER BY, use `multiSelectByMerge()`.

`multiSelectByMerge()` transforms both sides into coroutines sorted by compatible ORDER BY lists. It may add ORDER BY terms so duplicate-sensitive operators compare complete result rows, builds merge and duplicate-removal `KeyInfo`, splits long UNION/UNION ALL chains for balanced merging, and emits subroutines for out-A, out-B, EOF-A, EOF-B, A-less-than-B, A-equals-B, and A-greater-than-B. Duplicate suppression for UNION/EXCEPT/INTERSECT happens in `generateOutputSubroutine()` using a previous-output register vector.

Subquery flattening begins with a conservative gate in `flattenSubquery()`. It rejects combinations involving DISTINCT, recursive CTEs, disallowed LIMIT/OFFSET interactions, aggregate subqueries, unsafe LEFT/RIGHT/FULL join positions, compound operators other than UNION ALL, window functions, incompatible compound affinities, materialized CTEs, and ORDER BY/LIMIT cases that would change semantics. If permitted, it detaches the subquery, optionally clones parent SELECT arms for compound-subquery flattening, transfers subquery FROM items into the parent, moves subquery WHERE and ORDER BY terms, substitutes subquery result expressions for parent references through `SubstContext`, preserves outer-join nullability with `TK_IF_NULL_ROW` wrappers, recomputes column-use masks, and schedules obsolete transient tables for cleanup.

Predicate and expression rewrites are walker-based. Constant propagation discovers top-level AND-connected `COLUMN=CONSTANT` terms using binary collation and no value affinity, then replaces other matching column references with `EP_FixedCol` links to duplicated constants. WHERE pushdown tests whether an outer WHERE term is a single-table constraint for a subquery, respects join-origin flags and RIGHT/FULL join barriers, handles compound collation restrictions, rewrites the expression through the subquery result list, and appends it to the subquery WHERE or HAVING. `havingToWhere()` moves GROUP BY-compatible HAVING terms earlier so the WHERE planner can use them.

CTE resolution happens during expansion. `resolveFromTermToCte()` searches the active WITH stack, creates an ephemeral `Table` for a matched CTE, attaches a copied SELECT, records shared `CteUse`, checks `INDEXED BY` misuse, detects recursive references in eligible UNION/UNION ALL compounds, assigns a recursive cursor, walks non-recursive or anchor terms, validates explicit CTE column lists, and sets temporary circular-reference errors while walking to catch illegal recursion.

Aggregate helper flow starts after name resolution and aggregate analysis. `analyzeAggFuncArgs()` scans aggregate argument, aggregate-local ORDER BY, and filter expressions while `NC_InAggFunc` prevents recursive misclassification. `assignAggregateRegisters()` freezes `AggInfo` layout by assigning a contiguous register block. `resetAccumulator()` NULLs that block and opens ephemeral tables for DISTINCT aggregates and ordered aggregates. `updateAccumulator()` evaluates arguments, applies FILTER and DISTINCT, stores ordered-aggregate inputs into ephemeral sort tables or emits `OP_AggStep`, and populates non-aggregate accumulator columns. `finalizeAggFunctions()` replays ordered aggregate inputs before `OP_AggFinal` and preserves value subtypes when needed.

## State And Persistence Behavior

This code mostly mutates parser, AST, and generated-bytecode state. It does not directly write database pages. Persistent database access occurs later through VDBE programs emitted here.

- `Select` trees own `pEList`, `pSrc`, WHERE/GROUP/HAVING/ORDER/LIMIT expressions, WITH clauses, window lists, and compound links. Routines often detach these pointers temporarily and must restore or transfer ownership precisely.
- `Parse.nSelect`, `Parse.nTab`, and `Parse.nMem` are monotonically advanced for SELECT ids, VDBE cursors, and register high-water marks.
- `SelectDest` carries destination kind, cursor/register parameters, result-register ranges, affinity strings, bloom-filter cursors, and queue ORDER BY metadata between codegen layers.
- Join normalization mutates `Select.pWhere`, clears moved `SrcItem.u3.pOn`, marks `SrcItem.fg.isOn`, creates synthesized USING lists, marks nested result columns used, and sets expression flags such as `EP_OuterON`, `EP_InnerON`, `EP_CanBeNull`, and `EP_NoReduce`.
- DISTINCT and aggregate DISTINCT use ephemeral VDBE indexes. Their open opcodes can be patched later when planner knowledge makes them unnecessary.
- Sorters use ephemeral cursors, pseudo cursors, record layouts defined by ORDER keys, optional sequence fields, payload columns, deferred primary keys, and `KeyInfo` objects with reference counting.
- Recursive CTE state lives in ephemeral Queue, Distinct, and Current pseudo-table cursors. `CteUse` tracks materialization preference and use count for CTE references.
- Result metadata is stored in VDBE column names and transient `Table` objects. `Column.zCnName` may include hidden type text and collation metadata managed by column helpers.
- Flattening mutates source lists, SELECT flags, WHERE/ORDER/LIMIT pointers, cursor numbers, column-use bitmasks, and expression trees. Obsolete transient `Table` and `Select` objects are deferred through parser cleanup when still referenced by expressions.
- Constant propagation does not simply replace all columns with literal nodes. It marks columns with `EP_FixedCol` and stores the constant on `pLeft` to preserve comparison affinity and collation behavior.
- Aggregate state is represented by `AggInfo.aCol[]`, `AggInfo.aFunc[]`, `AggInfo.iFirstReg`, and per-function ephemeral cursor fields. The allocated accumulator registers persist for the generated VDBE statement, not database storage.

## Dependencies And Integration Points

- This file includes `sqliteInt.h` and integrates with nearly every core SQLite subsystem: parser state, expression trees, name resolution, authorization, schema lookup, virtual tables, VDBE bytecode, WHERE planning, window functions, CTEs, and aggregate analysis.
- Expression helpers from `expr.c` are heavily used: expression/list allocation and deletion, duplication, comparison, collation/affinity lookup, aggregate analysis wrappers, constant/group-by tests, single-table-constraint tests, and code generation.
- Source-list and table helpers provide cursor assignment, table/view lookup, subquery attachment/detachment, CTE metadata, column flags, hidden-column checks, primary-key metadata, and virtual-table safety checks.
- VDBE integration is central. The code emits opcodes such as `OP_OpenEphemeral`, `OP_OpenPseudo`, `OP_MakeRecord`, `OP_IdxInsert`, `OP_SorterInsert`, `OP_Sort`, `OP_SorterSort`, `OP_Yield`, `OP_InitCoroutine`, `OP_AggStep`, `OP_AggFinal`, `OP_OffsetLimit`, and many conditional jumps.
- WHERE integration appears through `WHERE_DISTINCT_*`, `WHERE_ORDERBY_*`, ORDER BY satisfaction counts, sorter LIMIT labels from the WHERE layer, and query planner flags such as `SF_FixedLimit`.
- Authorization integrates through `sqlite3AuthCheck()` for SELECT and recursive CTE processing, and view access may be blocked unless view support/trusted schema settings allow it.
- Window-function support is conditional. The chunk blocks flattening and recursive CTE cases that would change window semantics, and pushdown uses partition checks when safe.
- Compile-time options change behavior: `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_OMIT_CTE`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_VIEW`, `SQLITE_ENABLE_SORTER_REFERENCES`, `SQLITE_ENABLE_COLUMN_METADATA`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ALLOW_ROWID_IN_VIEW`, and debug/tree-trace flags all guard meaningful branches.
- EXPLAIN QUERY PLAN support is woven through sorter, compound, recursive CTE, simple count, DISTINCT aggregate, and ordered aggregate paths.

## Risks And Edge Cases

- Join flags are semantic guardrails. Clearing, moving, or failing to preserve `EP_OuterON`, `EP_InnerON`, `w.iJoin`, or `EP_CanBeNull` can change LEFT/RIGHT/FULL join answers by filtering rows before NULL-row generation.
- NATURAL and USING joins intentionally ignore hidden columns in synthesized USING lists, but explicit USING validation has different behavior. RIGHT/FULL joins add further ambiguity checks and coalesce handling.
- Column-name generation is intentionally conservative for legacy compatibility. Small changes can break applications that rely on undocumented name choices.
- DISTINCT handling depends on planner-selected ordering. Ordered DISTINCT must initialize previous-row registers so a first row of all NULL values is still emitted.
- Sorter record layout is fragile because ORDER-key columns, sequence fields, payloads, omitted ORDER BY references, deferred row-load keys, and subtype fields are all position-dependent.
- LIMIT/OFFSET registers are reused across UNION ALL arms and combined into LIMIT+OFFSET registers for sorter pruning. Incorrect reuse or early deletion can drop or duplicate rows.
- Compound merge correctness depends on matching collations and result-column mappings. `convertCompoundSelectToSubquery()` exists because ORDER BY COLLATE can otherwise make the merge algorithm compare different semantics.
- Recursive CTE execution assumes exactly one recursive table reference in a recursive term. The resolver detects multiple references and illegal recursive references in subqueries.
- Flattening has many negative restrictions because it is easy to move LIMIT, ORDER BY, aggregate, DISTINCT, window, or outer-join semantics across a boundary where results change.
- Constant propagation is affinity-sensitive. The `EP_FixedCol` representation and BLOB-affinity restrictions prevent false positives involving text/numeric conversion and LIKE/IS comparisons.
- WHERE pushdown through compounds with UNION/INTERSECT/EXCEPT is blocked for non-BINARY result collations because duplicate and set semantics could change.
- Aggregate ORDER BY defers `OP_AggStep`, so DISTINCT handling, payload layout, sequence uniqueness, subtype preservation, and final replay order must remain consistent.
- The chunk ends mid-`countOfViewOptimization()`. Only the initial eligibility checks are visible here; the transformation body and cleanup behavior must be read in the next chunk before modifying that optimization.

## Test Signals

- Join tests should cover NATURAL, USING, ON, LEFT, RIGHT, FULL, hidden columns, ambiguous USING names, nested FROM clauses, and virtual table ON-clause movement.
- DISTINCT tests should cover unordered DISTINCT, ordered DISTINCT with NULL rows, DISTINCT satisfied by uniqueness, DISTINCT plus OFFSET, and DISTINCT aggregate argument-count errors.
- ORDER BY tests should cover full sorter use, partially index-satisfied ORDER BY prefixes, LIMIT/OFFSET bounded sorting, sorter-reference builds, omitted ORDER BY references, and SRT_Table/EphemTab/Set/Mem/Coroutine destinations.
- Compound SELECT tests should cover VALUES compounds, UNION ALL with LIMIT/OFFSET reuse, UNION/EXCEPT/INTERSECT duplicate suppression, ORDER BY COLLATE rewrites, balanced merge chains, and mismatched result-column-count errors.
- Recursive CTE tests should cover FIFO and ORDER BY queues, UNION duplicate suppression, LIMIT/OFFSET, authorization, recursive aggregate/window rejection, multiple recursive references, and circular references.
- Flattening tests should cover every documented restriction, especially LIMIT with parent WHERE/aggregate/join, LEFT/RIGHT/FULL joins, compound UNION ALL flattening, materialized CTE blocking, window functions, and affinity mismatches.
- Predicate pushdown tests should include aggregate subqueries, HAVING insertion, window PARTITION BY safety, compound collation barriers, RIGHT/FULL join barriers, VALUES subqueries, and `rowid ISNULL` view compatibility builds.
- Constant propagation tests should include text/numeric affinity counterexamples, BLOB-affinity LIKE cases, collations other than BINARY, outer-join ON terms, and repeated propagation until fixed point.
- Metadata tests should verify AS names, short/full column-name pragmas, rowid naming, view/subquery origin metadata, CTE explicit column counts, and subquery column type/collation inference.
- Aggregate tests should cover simple `count(*)`, min/max optimization, GROUP BY with indexed expressions, DISTINCT aggregates, ordered aggregates with duplicate keys, subtype-bearing values, FILTER clauses, and HAVING-to-WHERE movement.
- OOM and debug builds should exercise cleanup paths for detached subqueries, parser cleanup registration, `KeyInfo` refcounts, transient table lifetimes after flattening, and VDBE scanstatus/treetrace guarded paths.

### subset-b-008785: lines 7154-8967

# sources/storage-engines/sqlite/src/select.c lines 7154-8967

## Scope

This chunk covers the tail of the count-of-view rewrite, helper logic for SELECT aliases, FROM-subquery coroutine eligibility, EXISTS-to-JOIN rewriting, ON-clause validation, sort-order copying, and most of `sqlite3Select()`. The `sqlite3Select()` span includes name/prep handling, FROM-clause optimizations, compound SELECT dispatch, constant propagation, subquery implementation as coroutines/materialized tables/reused CTEs or views, DISTINCT/ORDER BY setup, non-aggregate row loops, aggregate and GROUP BY bytecode generation, simple `count(*)` and min/max fast paths, final sorting, cleanup, and debug self-checks.

## Purpose

- Rewrite simple `count(*)` over UNION ALL views into a sum of scalar subquery counts when all participating SELECTs are non-aggregate, non-DISTINCT, and unfiltered.
- Reject ambiguous `UPDATE ... FROM` source aliases before query flattening can make them harder to diagnose.
- Decide whether FROM-clause subqueries can be streamed as VDBE coroutines or must be materialized.
- Convert eligible `WHERE EXISTS (SELECT ...)` predicates into joined FROM terms with `fromExists` loop semantics.
- Validate that ON clauses and table-valued function arguments on outer joins do not reference tables to their right.
- Drive the main SELECT code-generation pipeline from resolved syntax tree to VDBE bytecode and query-plan annotations.
- Coordinate planner flags for DISTINCT, ORDER BY, GROUP BY, LIMIT, aggregate DISTINCT, min/max, and output destinations.

## Important APIs, Types, And Functions

- `countOfViewOptimization(Parse*, Select*)` is entered before this chunk and completed here. It detaches a UNION ALL subquery from the FROM item, rewrites each compound arm into `SELECT count(*) ...`, combines them with `TK_PLUS`, and clears the outer `SF_Aggregate` flag.
- `sameSrcAlias(SrcItem*, SrcList*)` recursively checks a FROM list and nested `SF_NestedFrom` subqueries for another source using the same schema table and alias.
- `fromClauseTermCanBeCoroutine(Parse*, SrcList*, int, int)` decides whether a FROM subquery may be implemented using `SRT_Coroutine`. It rejects materialized or multiply used CTEs, right-join left operands, disabled coroutine optimization, self-joined views, UPDATE FROM cases, and join-order positions that cannot safely be outer loops.
- `existsToJoin(Parse*, Select*, Expr*)` recursively walks top-level AND terms in a WHERE clause and rewrites eligible `TK_EXISTS` nodes into joined FROM terms.
- `CheckOnCtx` carries the active `SrcList`, RHS join cursor limit, table-function argument mode, and parent nested SELECT context for ON-clause validation.
- `selectCheckOnClausesExpr()` and `selectCheckOnClausesSelect()` are walker callbacks that detect invalid references to right-side tables in outer-join ON constraints and nested SELECT contexts.
- `sqlite3SelectCheckOnClauses(Parse*, Select*)` is the public validator called after ON constraints have been moved into WHERE with `SF_OnToWhere`.
- `sqlite3CopySortOrder(ExprList*, ExprList*)` copies DESC sort bits between parallel expression lists. It is used for DISTINCT-to-GROUP-BY and GROUP-BY/ORDER-BY equivalence checks.
- `sqlite3Select(Parse*, Select*, SelectDest*)` is the main SELECT bytecode generator. Its output behavior is controlled by `SelectDest` destinations such as `SRT_Output`, `SRT_EphemTab`, `SRT_Coroutine`, queues, EXISTS, discard, and aggregate inner destinations.
- Major state types in this chunk include `Select`, `SrcList`, `SrcItem`, `Subquery`, `CteUse`, `Expr`, `ExprList`, `AggInfo`, `DistinctCtx`, `SortCtx`, `WhereInfo`, `NameContext`, `Vdbe`, `KeyInfo`, `Table`, and `Index`.

## Control Flow

The count-of-view tail first validates every UNION ALL arm, rejecting WHERE, LIMIT, aggregate, and DISTINCT subqueries. It then detaches the compound subquery, deletes the original outer FROM list, creates an empty one-source list, rewrites each arm as an aggregate count SELECT, wraps each arm in a scalar `TK_SELECT` expression, and chains the scalar counts with `TK_PLUS`. Ownership of old expression lists and SELECT nodes is transferred to parser cleanup hooks so early cleanup remains safe.

`fromClauseTermCanBeCoroutine()` is a pure eligibility gate used later by `sqlite3Select()`. It handles CTE materialization policy first, then global join/optimization exclusions, then join-position tests. A leftmost single FROM term or leftmost term followed by CROSS JOIN can stream. A later term can stream only if no earlier term is another subquery and intervening join flags do not force an incompatible outer or CROSS join order.

`existsToJoin()` only runs when parsing saw EXISTS and the optimizer flag is enabled. It ignores ON-clause expression trees, requires available FROM bitmap space, and avoids OFFSET-containing LIMITs. For each eligible EXISTS subquery, it requires one non-subquery FROM item, no aggregate, no LIMIT, and no compound. It allocates a cursor renumbering map so copied EXISTS expressions get unique cursor numbers, turns the original EXISTS expression into integer `1`, appends the subquery source to the outer FROM list, marks the new source `fromExists`, moves the subquery WHERE term into the outer WHERE with AND, and schedules the now-empty subquery for cleanup.

ON-clause checking starts from `sqlite3SelectCheckOnClauses()`. The expression walker treats `EP_OuterON` expressions and `EP_InnerON` expressions inside FROM lists containing RIGHT/FULL joins as roots that must be checked. While an `iJoin` cursor limit is active, `TK_COLUMN` nodes are resolved against the current or parent `CheckOnCtx`; if the referenced cursor is greater than the join RHS cursor, the parser emits either "ON clause references tables to its right" or "table-function argument references tables to its right". Nested SELECTs get their own child context and have `SF_OnToWhere` cleared after validation.

`sqlite3Select()` begins with authorization and optional tree tracing. During tag-select-0100 it drops DISTINCT and ORDER BY when the destination can ignore them, runs `sqlite3SelectPrep()`, checks duplicate UPDATE FROM target aliases with `sameSrcAlias()`, emits column names for `SRT_Output`, rewrites window queries, and snapshots core local pointers.

The first FROM scan performs join and subquery optimizations. OUTER JOIN strength reduction changes LEFT/FULL/RIGHT join flags when WHERE terms imply the nullable side cannot actually be NULL. For subqueries, it checks view column counts, respects materialized CTE optimization fences, skips aggregate subquery flattening, removes harmless subquery ORDER BY clauses when allowed, preserves ORDER BY/LIMIT coroutine behavior for complex outer result sets, and calls `flattenSubquery()`. If the SELECT is compound after this, control returns through `multiSelect()`.

Before generating the main loops, `sqlite3Select()` attempts EXISTS-to-JOIN, WHERE constant propagation, and count-of-view rewriting. It then performs a second FROM scan to authorize unreferenced tables and generate bytecode for FROM subqueries. Subqueries are implemented as one of four paths: coroutine (`OP_InitCoroutine`, recursive `sqlite3Select()` with `SRT_Coroutine`, `OP_EndCoroutine`), already materialized CTE reuse (`OP_Gosub`, `OP_OpenDup`), self-join view reuse (`OP_Gosub` and `OP_OpenDup` from the prior source), or materialization into an ephemeral table via `SRT_EphemTab`, optionally guarded by `OP_Once` for uncorrelated subqueries. The code records CTE materialization addresses and cursor metadata for later reuses.

After FROM analysis, DISTINCT plus ORDER BY can be transformed into GROUP BY if the select list and ORDER BY list match and there are no aggregate/window blockers. The function then opens a provisional ORDER BY ephemeral index or sorter, opens destination ephemeral tables for `SRT_EphemTab`, computes LIMIT/OFFSET registers, and opens a DISTINCT ephemeral index if needed.

For non-aggregate SELECTs without GROUP BY, the function calls `sqlite3WhereBegin()` with ORDER BY and DISTINCT hints, adjusts `nSelectRow`, records whether WHERE satisfied DISTINCT or ORDER BY, no-ops unused sort opens, and emits either the window step path or the standard `selectInnerLoop()` followed by `sqlite3WhereEnd()`.

Aggregate handling first clears aliases between the result list and GROUP BY, estimates output rows, allocates `AggInfo`, and analyzes aggregate columns/functions across the result list, ORDER BY, HAVING, and aggregate arguments. HAVING terms that can be pushed to WHERE are handled by `havingToWhere()`. For a single aggregate without GROUP BY/HAVING, `minMaxQuery()` may synthesize a one-term ORDER BY to let WHERE choose an early-out min/max plan.

GROUP BY aggregate code opens a sorter cursor speculatively, allocates accumulator and comparison registers, and calls `sqlite3WhereBegin()` with GROUP BY, DISTINCT, and sort-by-group flags. If WHERE can deliver rows in group order, the sorter open is converted to a no-op later. Otherwise, it writes group keys and needed aggregate columns into the sorter with `OP_MakeRecord` and `OP_SorterInsert`, then reads sorted records back through `OP_SorterData` and an `OP_OpenPseudo` cursor. The loop compares current group registers against prior group registers with `OP_Compare`/`OP_Jump`, emits the prior group through an output subroutine on group change, resets accumulators, updates accumulators for the current row, and finally emits the last group. Separate subroutines handle output, HAVING filtering, destination emission, abort signaling, and accumulator reset.

Non-GROUP aggregate code has two major paths. `isSimpleCount()` enables a direct `SELECT count(*) FROM table` fast path: it verifies schema and table locks, chooses a smaller usable non-partial ordered index when possible, opens a read cursor, emits `OP_Count` into the aggregate result register, closes the cursor, and annotates the plan. Otherwise, the general aggregate path resets accumulators, optionally prepares a first-row accumulator guard register, passes min/max or aggregate-DISTINCT hints to `sqlite3WhereBegin()`, calls `updateAccumulator()`, patches distinct ephemeral opens with `fixDistinctOpenEph()`, emits min/max early-out if selected, finalizes aggregate functions, evaluates HAVING, and calls `selectInnerLoop()` once for the single aggregate output row.

The tail explains unordered DISTINCT temp tables, emits deferred ORDER BY output with `generateSortTail()`, resolves the query end label, sets the return code from `Parse.nErr`, frees synthesized min/max ORDER BY lists, runs debug `AggInfo` consistency checks, pops explain-plan context, and returns.

## State And Persistence Behavior

This code does not directly persist rows into user tables except through emitted VDBE programs whose destinations may write into temporary or caller-provided destinations. Its direct mutations are mostly parser and bytecode-generation state:

- `Select.selFlags` is rewritten for DISTINCT elimination, aggregate conversion, count-of-view, `SF_UFSrcCheck`, `SF_OnToWhere`, `SF_PushDown`, and DISTINCT-to-GROUP-BY.
- `Select.pSrc`, `Select.pWhere`, `Select.pGroupBy`, `Select.pOrderBy`, `Select.pEList`, `Select.nSelectRow`, `Select.iLimit`, and subquery SELECT fields are mutated as optimizations rewrite the tree.
- `SrcItem.fg.jointype` is changed by OUTER JOIN strength reduction. `SrcItem.fg.fromExists`, `viaCoroutine`, and `isMaterialized` record later WHERE-loop and scan behavior.
- `Subquery.addrFillSub`, `regReturn`, and `regResult` capture coroutine/materialization subprogram entry points and output registers.
- `CteUse.addrM9e`, `regRtn`, `iCur`, and `nRowEst` cache uncorrelated CTE materialization bytecode for reuse.
- `Parse.nTab` allocates VDBE cursor numbers for subqueries, sorters, DISTINCT tables, GROUP BY sorters, simple count cursors, and pseudo tables.
- `Parse.nMem` allocates VDBE registers for coroutine returns, LIMIT registers, group key comparisons, abort/use flags, accumulator state, output subroutine return addresses, and min/max/aggregate guards.
- `AggInfo` records aggregate columns, functions, accumulator registers, sorting cursor metadata, GROUP BY expression linkage, and debug back-pointers. It is registered with parser cleanup via `agginfoFree()`.
- Ephemeral b-trees and sorters are opened in generated bytecode for ORDER BY, DISTINCT, GROUP BY, aggregate DISTINCT, subquery materialization, and `SRT_EphemTab` destinations. These are statement-local runtime structures, not durable database storage.
- Real database access is coordinated through schema verification, table locks, read authorization callbacks, `sqlite3WhereBegin()` scan plans, and `OP_OpenRead` in the simple-count fast path.

## Dependencies And Integration Points

- Name resolution, SELECT expansion, window rewrite, and ON-to-WHERE movement must run before much of this chunk. The public ON-clause checker is called from `resolve.c`.
- Authorization uses `sqlite3AuthCheck()` both for SELECT authorization and for empty-column READ callbacks on unreferenced tables.
- Optimizer feature flags include `SQLITE_Coroutines`, `SQLITE_ExistsToJoin`, `SQLITE_PropagateConst`, `SQLITE_QueryFlattener`, `SQLITE_CountOfView`, `SQLITE_SimplifyJoin`, `SQLITE_OmitOrderBy`, `SQLITE_NullUnusedCols`, `SQLITE_PushDown`, and `SQLITE_GroupByOrder`.
- Query planner integration is through `sqlite3WhereBegin()`, `sqlite3WhereEnd()`, `sqlite3WhereIsOrdered()`, `sqlite3WhereIsSorted()`, `sqlite3WhereIsDistinct()`, `sqlite3WhereOutputRowCount()`, `sqlite3WhereOrderByLimitOptLabel()`, and `sqlite3WhereMinMaxOptEarlyOut()`.
- WHERE and WHERE-code paths consume `SrcItem.fg.fromExists` to lower row estimates and exit the EXISTS-derived loop after the first match.
- Expression infrastructure supplies aggregate analysis, HAVING pushdown, constant propagation, implication checks for non-null join rows, expression code generation, expression-list comparison, sort key metadata, cleanup registration, and tree walking.
- VDBE integration uses opcodes including `OP_InitCoroutine`, `OP_EndCoroutine`, `OP_Gosub`, `OP_Return`, `OP_OpenDup`, `OP_Once`, `OP_OpenEphemeral`, `OP_SorterOpen`, `OP_SorterInsert`, `OP_SorterSort`, `OP_SorterData`, `OP_SorterNext`, `OP_OpenPseudo`, `OP_MakeRecord`, `OP_Compare`, `OP_Jump`, `OP_IfPos`, `OP_Integer`, `OP_Null`, `OP_OpenRead`, `OP_Count`, `OP_Close`, and `OP_Goto`.
- Explain and scan-status integration uses `ExplainQueryPlan`, `ExplainQueryPlan2`, `ExplainQueryPlanPop`, `sqlite3VdbeScanStatusCounters()`, and `sqlite3VdbeScanStatusRange()`.
- Debug/tracing hooks include `TREETRACE`, `sqlite3TreeViewSelect()`, `sqlite3ShowSelect()`, `printAggInfo()`, `testcase()`, `VdbeCoverage()`, and final `AggInfo` assertions.

## Risks And Edge Cases

- The count-of-view rewrite is only correct for UNION ALL, not UNION, DISTINCT, aggregate, filtered, limited, grouped, or HAVING-bearing arms. The explicit DISTINCT exclusion addresses a 2025 forum-post regression note in the source comment.
- Cursor renumbering in EXISTS-to-JOIN is critical because EXISTS expressions may be copied. Reusing a cursor number could bind moved predicates to the wrong table instance.
- `fromExists` changes WHERE-loop semantics to one-match behavior. If the rewrite admits a subquery with duplicate-sensitive semantics, results can change.
- ON-clause validation compares cursor numbers, so it depends on cursor allocation preserving FROM-order assumptions for the relevant source list and nested contexts.
- Materialized CTE policy must respect `AS MATERIALIZED`, multiple references, and `NOT MATERIALIZED`; otherwise optimization fences and reuse semantics break.
- Coroutine eligibility is tightly coupled to join order. Streaming a subquery that cannot be the outer loop can make generated bytecode request rows in an invalid order.
- OUTER JOIN strength reduction must clear or preserve join expression annotations consistently with `unsetJoinExpr()`, especially around RIGHT and FULL joins.
- Subquery ORDER BY removal is deliberately conservative around LIMIT, window rewrites, UPDATE FROM, aggregates other than simple count/min/max, joins, and recursive CTEs. Removing ORDER BY from one of those cases can affect observable behavior.
- The DISTINCT-to-GROUP-BY rewrite relies on copied sort order and structural equality. Collation or DESC mismatches would cause wrong result order or duplicate handling.
- Many `OP_OpenEphemeral`/`OP_SorterOpen` instructions are emitted speculatively and later changed to no-ops. Missed no-op conversion is usually a performance issue, but premature conversion is a correctness bug.
- GROUP BY code has two very different input paths: planner-ordered rows and sorter-ordered rows. Register layout for group keys and aggregate columns must stay aligned across both.
- Aggregate DISTINCT optimization builds composite distinct keys from GROUP BY plus the aggregate argument. Incorrect `pDistinct` construction or `fixDistinctOpenEph()` patching can over-count or under-count per group.
- The simple `count(*)` path must avoid unordered and partial indexes and respect `NOT INDEXED`; otherwise `OP_Count` could scan an incomplete or unsuitable b-tree.
- The min/max path depends on WHERE ordering flags and early-out support. It must still finalize aggregates correctly for empty inputs and FILTER/min/max interactions.
- Cleanup paths assume parser cleanup hooks own allocations such as detached expression lists, rewritten SELECT nodes, and `AggInfo`. Early exits must leave `Parse.nHeight` and `zAuthContext` restored after subquery generation.

## Test Signals

- `sources/storage-engines/sqlite/test/countofview.test` and the count-of-view cases in `pushdown.test` are direct signals for the UNION ALL count rewrite, including CTE and HAVING disqualifiers.
- `join2.test`, `join8.test`, `joinH.test`, and `joinI.test` cover ON-clause right-reference errors for RIGHT/FULL/outer joins.
- `tabfunc01.test` and `carray01.test` cover the table-function argument variant of the same right-reference validation.
- `count.test` and `eqp.test` cover `OP_Count` behavior and explain-query-plan output for simple `SELECT count(*) FROM tbl` plans.
- `select5.test`, `select6.test`, `select7.test`, `distinctagg.test`, `orderby1.test`, `orderby2.test`, `orderby4.test`, and `distinct2.test` exercise GROUP BY, HAVING, DISTINCT, ORDER BY elimination, DISTINCT-to-GROUP-BY, and aggregate DISTINCT paths.
- `joinE.test` and related RIGHT/FULL JOIN tests are key signals for strength reduction and join flag preservation.
- `with*.test` files, especially materialized/NOT MATERIALIZED CTE cases, should exercise CTE materialization reuse and coroutine/materialization choices.
- EQP assertions containing `CO-ROUTINE`, `MATERIALIZE`, `USE TEMP B-TREE FOR GROUP BY`, `USE TEMP B-TREE FOR DISTINCT`, and `USE TEMP B-TREE FOR ORDER BY` are useful for detecting plan-shape regressions in this chunk.
- Optimizer-disabling tests through `SQLITE_TESTCTRL_OPTIMIZER` names such as `groupby-order`, `exists-to-join`, `count-of-view`, `omit-orderby`, and `simplify-join` should preserve both results and expected plan changes when individual optimizations are disabled.
- OOM and fault-injection tests around SELECT preparation, subquery materialization, expression duplication, sorter/key-info allocation, and aggregate analysis should verify that `select_end` cleanup remains balanced and no parser state is left inconsistent.
