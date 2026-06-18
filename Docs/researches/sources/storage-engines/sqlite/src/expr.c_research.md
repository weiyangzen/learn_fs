# Research: sources/storage-engines/sqlite/src/expr.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008769`: lines 1-7506, `Docs/researches/chunks/subset-b-008769_research.md`
- `subset-b-008770`: lines 7507-7727, `Docs/researches/chunks/subset-b-008770_research.md`

## Chunk Research

### subset-b-008769: lines 1-7506

# sources/storage-engines/sqlite/src/expr.c lines 1-7506

## Scope

This chunk covers almost all of SQLite's expression-analysis and expression-code-generation implementation up to the middle of aggregate-function discovery. It starts with expression affinity, collation, comparison, vector, and tree-height helpers; continues through expression allocation, deletion, duplication, expression-list/source-list/select cloning, list construction, constant/nullability analysis, rowid helpers, `IN` and subquery code generation, scalar expression bytecode emission, boolean jump emission, expression comparison, implication analysis, covering-index/reference walkers, and aggregate `AggInfo` setup; and ends inside the `TK_AGG_FUNCTION` branch of `analyzeAggregate()`.

The remaining aggregate-analysis cases, the public aggregate walker entry points, and temporary register helpers continue after this chunk and are intentionally out of scope for this document.

## Purpose

- Determine expression type affinity, possible result data types, and collating sequences so comparisons and index choices follow SQLite SQL semantics.
- Build, connect, duplicate, reduce, and delete `Expr`, `ExprList`, `SrcList`, `IdList`, `Select`, `With`, and window-bearing expression trees during parsing, schema loading, and code generation.
- Generate VDBE bytecode for scalar expressions, column reads, generated columns, constants, functions, `CASE`, `BETWEEN`, `IN`, scalar subqueries, `EXISTS`, trigger pseudo-table references, `RAISE()`, vector comparisons, and boolean branches.
- Implement optimizer support checks for constants, table-local constraints, nullability, expression equality, expression implication, covering indexes, expression indexes, partial-index substitutions, and join simplification.
- Build or locate efficient RHS access paths for `IN` operators, including rowid lookup, existing-index lookup, reusable subroutines, ephemeral tables, and optional Bloom-filter support.
- Initialize aggregate-analysis state by mapping aggregate input columns and aggregate functions into `AggInfo` arrays for later aggregate code generation.

## Important APIs, Types, And Functions

- Affinity/collation helpers: `sqlite3TableColumnAffinity()`, `sqlite3ExprAffinity()`, `sqlite3ExprDataType()`, `sqlite3ExprAddCollateToken()`, `sqlite3ExprSkipCollate()`, `sqlite3ExprCollSeq()`, `sqlite3ExprNNCollSeq()`, `sqlite3CompareAffinity()`, `sqlite3IndexAffinityOk()`, `sqlite3BinaryCompareCollSeq()`, `sqlite3ExprCompareCollSeq()`, and `codeCompare()`.
- Vector helpers: `sqlite3ExprIsVector()`, `sqlite3ExprVectorSize()`, `sqlite3VectorFieldSubexpr()`, `sqlite3ExprForVectorField()`, `exprVectorRegister()`, `exprCodeVector()`, `codeVectorCompare()`, `sqlite3ExprListToValues()`, and `sqlite3ExprListAppendVector()`.
- Tree construction and lifetime helpers: `sqlite3ExprAlloc()`, `sqlite3Expr()`, `sqlite3ExprInt32()`, `sqlite3ExprAttachSubtrees()`, `sqlite3PExpr()`, `sqlite3PExprAddSelect()`, `sqlite3ExprAnd()`, `sqlite3ExprFunction()`, `sqlite3ExprAddFunctionOrderBy()`, `sqlite3ExprAssignVarNumber()`, `sqlite3ExprDelete()`, `sqlite3ExprDeferredDelete()`, `sqlite3ExprUnmapAndDelete()`, and `sqlite3ClearOnOrUsing()`.
- Duplication helpers: `exprStructSize()`, `dupedExprStructSize()`, `dupedExprNodeSize()`, `dupedExprSize()`, `exprDup()`, `sqlite3ExprDup()`, `sqlite3ExprListDup()`, `sqlite3SrcListDup()`, `sqlite3IdListDup()`, `sqlite3SelectDup()`, `sqlite3WithDup()`, and `gatherSelectWindows()`.
- Expression-list helpers: `sqlite3ExprListAppendNew()`, `sqlite3ExprListAppendGrow()`, `sqlite3ExprListAppend()`, `sqlite3ExprListSetSortOrder()`, `sqlite3ExprListSetName()`, `sqlite3ExprListSetSpan()`, `sqlite3ExprListCheckLength()`, `sqlite3ExprListDelete()`, and `sqlite3ExprListFlags()`.
- Constant and semantic-analysis helpers: `sqlite3SelectWalkFail()`, `sqlite3IsTrueOrFalse()`, `sqlite3ExprIdToTrueFalse()`, `sqlite3ExprTruthValue()`, `sqlite3ExprSimplifiedAndOr()`, `exprNodeIsConstant()`, `sqlite3ExprIsConstant()`, `sqlite3ExprIsSingleTableConstraint()`, `sqlite3ExprIsConstantOrGroupBy()`, `sqlite3ExprIsConstantOrFunction()`, `sqlite3ExprIsInteger()`, `sqlite3ExprCanBeNull()`, `sqlite3ExprNeedsNoAffinityChange()`, `sqlite3IsRowid()`, and `sqlite3RowidAlias()`.
- `IN`/subquery helpers: `isCandidateForInOpt()`, `sqlite3SetHasNullFlag()`, `sqlite3InRhsIsConstant()`, `sqlite3FindInIndex()`, `exprINAffinity()`, `sqlite3SubselectError()`, `sqlite3VectorErrorMsg()`, `findCompatibleInRhsSubrtn()`, `sqlite3CodeRhsOfIN()`, `sqlite3CodeSubselect()`, `sqlite3ExprCheckIN()`, and `sqlite3ExprCodeIN()`.
- Main bytecode emission helpers: `codeReal()`, `codeInteger()`, `sqlite3ExprCodeLoadIndexColumn()`, `sqlite3ExprCodeGeneratedColumn()`, `sqlite3ExprCodeGetColumnOfTable()`, `sqlite3ExprCodeGetColumn()`, `sqlite3ExprCodeMove()`, `sqlite3ExprToRegister()`, `exprCodeInlineFunction()`, `sqlite3IndexedExprLookup()`, `exprPartidxExprLookup()`, `exprCodeTargetAndOr()`, `sqlite3ExprCodeTarget()`, `sqlite3ExprCodeRunJustOnce()`, `sqlite3ExprNullRegisterRange()`, `sqlite3ExprCodeTemp()`, `sqlite3ExprCode()`, `sqlite3ExprCodeCopy()`, `sqlite3ExprCodeFactorable()`, `sqlite3ExprCodeExprList()`, and `exprCodeBetween()`.
- Boolean and comparison helpers: `sqlite3ExprIfTrue()`, `sqlite3ExprIfFalse()`, `sqlite3ExprIfFalseDup()`, `sqlite3ExprCompare()`, `sqlite3ExprListCompare()`, `sqlite3ExprCompareSkip()`, `sqlite3ExprImpliesExpr()`, `sqlite3ExprImpliesNonNullRow()`, `sqlite3ExprCoveredByIndex()`, and `sqlite3ReferencesSrcList()`.
- Aggregate setup helpers in this chunk: `agginfoPersistExprCb()`, `sqlite3AggInfoPersistWalkerInit()`, `addAggInfoColumn()`, `addAggInfoFunc()`, `findOrCreateAggInfoColumn()`, and the start of `analyzeAggregate()`.

Key local structures and state carriers include `Parse`, `Expr`, `ExprList`, `Select`, `SrcList`, `SrcItem`, `Table`, `Column`, `Index`, `FuncDef`, `CollSeq`, `NameContext`, `AggInfo`, `IndexedExpr`, `SubrtnSig`, `Walker`, `Vdbe`, and VDBE registers/cursors/labels.

## Control Flow

Expression construction starts in parser-facing helpers. `sqlite3ExprAlloc()` creates leaf nodes and may inline small integer literals through `EP_IntValue`. `sqlite3PExpr()` allocates operator nodes, attaches left/right subtrees, propagates flags, and checks expression depth. Function calls use `sqlite3ExprFunction()`, optional aggregate `ORDER BY` clauses are represented by a `TK_ORDER` node attached to the function expression, and subqueries are attached with `sqlite3PExprAddSelect()`.

Expression ownership is explicit. Delete paths walk right/select/list/window children, skip recursive deletion of `pLeft` for `TK_SELECT_COLUMN`, and use a tail-recursive restart optimization for unary left chains. Duplication can produce full or reduced/token-only trees; reduced copies use a single `EdupBuf` allocation for many `Expr` nodes and copied tokens and are guarded by flags such as `EP_Reduced`, `EP_TokenOnly`, `EP_Static`, and debug-only immutability markers.

Constant analysis is implemented as `Walker` passes with mode-specific `Walker.eCode` values. The same callback family distinguishes ordinary constants, constants not derived from outer joins, table-local row constants, DEFAULT expressions while parsing new DDL versus existing schema text, and constants/functions suitable for factoring. SELECT callbacks either abort on subqueries or allow uncorrelated subqueries depending on the caller.

`IN` processing first validates vector arity, computes an affinity string, and calls `sqlite3FindInIndex()`. That routine tries, in order, to use a direct rowid cursor, find a compatible existing index with matching affinity/collation/uniqueness requirements, skip b-tree construction for small or nonconstant list RHS values, or build an ephemeral table. `sqlite3CodeRhsOfIN()` emits reusable RHS materialization subroutines when possible, can reuse compatible prior subroutines by comparing `SubrtnSig`, and may attach a Bloom filter for membership probes. `sqlite3ExprCodeIN()` then emits SQLite's NULL-sensitive membership algorithm: handle trivial comparison lists, apply affinity and vector field reordering, detect NULLs on the LHS, probe rowid/index/ephemeral RHS storage, distinguish FALSE from NULL when needed, and perform a fallback scan for NULL-comparison results.

Scalar subqueries and `EXISTS` compile through `sqlite3CodeSubselect()`. The function emits an `OP_BeginSubrtn` block, wraps uncorrelated cases in `OP_Once`, initializes result registers to NULL or 0, forces an effective `LIMIT 1`, delegates to `sqlite3Select()`, caches the result register in `Expr.iTable`, and returns via `OP_Return`. Later encounters of the same expression call the subroutine with `OP_Gosub`.

The main expression emitter, `sqlite3ExprCodeTarget()`, dispatches on `Expr.op`. It handles direct register reuse, generated-column loops, expression-index lookups, partial-index constant substitutions, constants, bind parameters, column reads, casts, vector and scalar comparisons, boolean `AND`/`OR`, arithmetic, unary operations, truth tests, null tests, aggregate references, scalar/window/inline functions, subqueries, `IN`, `BETWEEN`, collation wrappers, trigger `old`/`new` references, `IF_NULL_ROW` guards for outer joins, `CASE`, and trigger-only `RAISE()`. Helpers such as `sqlite3ExprCode()`, `sqlite3ExprCodeTemp()`, and `sqlite3ExprCodeExprList()` wrap this with register allocation, copy-vs-scopy decisions, constant factoring, and list/ref-copy behavior.

Boolean branch generation avoids materializing boolean values when possible. `sqlite3ExprIfTrue()` and `sqlite3ExprIfFalse()` short-circuit `AND` and `OR`, invert comparisons by relying on aligned token/opcode numbers, handle `IS`/`IS NOT` with `SQLITE_NULLEQ`, call `sqlite3ExprCodeIN()` with separate false/null labels, expand `BETWEEN`, and otherwise emit `OP_If` or `OP_IfNot` over a computed register.

Optimizer predicates are conservative. `sqlite3ExprCompare()` proves expression equality only when it can do so safely, with special handling for top-level `COLLATE`, `TK_REGISTER`, aggregate columns, variables bound during reprepare, windows, flags, tokens, lists, and table aliases. Implication routines use this equality plus limited structural rules to prove `x IS NOT NULL`, OR implication, `iif()`/CASE implication, and whether a WHERE term makes a nullable-side join row impossible. Covering-index and source-reference checks use walkers that track column cursor ids and subquery-local exclusion lists.

Aggregate setup begins near the end of the chunk. `sqlite3AggInfoPersistWalkerInit()` prepares a walker that duplicates `AggInfo`-owned expressions if the original tree might change. `findOrCreateAggInfoColumn()` maps table columns into `AggInfo.aCol[]`, assigns grouping sorter columns, converts `TK_COLUMN` to `TK_AGG_COLUMN`, and writes `Expr.pAggInfo`/`iAgg`. `analyzeAggregate()` starts by recognizing indexed expressions inside aggregate functions and ordinary column references. The chunk ends while entering the new-aggregate-function allocation path, before the function entry is fully populated.

## State And Persistence Behavior

This file mostly mutates compiler and VDBE state, not persistent database pages. Persistent effects are indirect: the generated VDBE program later reads/writes tables, evaluates generated columns, enforces triggers, runs functions, and executes subqueries according to the compiled expression semantics.

Important transient state includes:

- `Expr` flags and fields such as `EP_Collate`, `EP_Skip`, `EP_Unlikely`, `EP_Subquery`, `EP_xIsSelect`, `EP_IntValue`, `EP_Leaf`, `EP_Reduced`, `EP_TokenOnly`, `EP_Static`, `EP_HasFunc`, `EP_Distinct`, `EP_WinFunc`, `EP_FromDDL`, `EP_OuterON`, `EP_InnerON`, `EP_Subrtn`, `EP_FixedCol`, `EP_FixedDest`, `EP_SubtArg`, `iTable`, `iColumn`, `op2`, `affExpr`, `pAggInfo`, and `iAgg`.
- `Parse` counters and caches such as `nMem`, `nTab`, `nVar`, `pVList`, `pConstExpr`, `pIdxEpr`, `pIdxPartExpr`, `iSelfTab`, `okConstFactor`, `withinRJSubrtn`, `mSubrtnSig`, error counters, and SQL variable masks.
- VDBE bytecode state: registers, cursors, labels, P4 collation/keyinfo/function payloads, `OP_Once`/subroutine blocks, `OP_OpenRead`, `OP_OpenEphemeral`, `OP_IdxInsert`, `OP_Found`/`OP_NotFound`, comparison opcodes, and scalar function calls.
- Schema object reference state during duplication, including `Table.nTabRef`, CTE use counts, copied `SrcList` flags, duplicated names/aliases, and window lists rebuilt for duplicated SELECTs.
- Aggregate state in `AggInfo.aCol[]` and `AggInfo.aFunc[]`, with expression nodes rewritten to aggregate-column/function references.

Durability-sensitive persistent behavior is controlled by the bytecode produced here rather than by direct writes in this chunk. For example, generated-column expressions may feed table writes elsewhere, trigger `RAISE()` can halt statements, and subquery/`IN` bytecode can open real table or index cursors, but this source range does not itself update database files.

## Dependencies And Integration Points

- Parser and resolver code create the `Expr` trees consumed here and rely on this file for allocation, expression-list metadata, variable numbering, function-call nodes, vector assignments, and error offsets.
- VDBE integration is central: almost every codegen path emits `sqlite3VdbeAddOp*()` instructions, labels, comments, P4 payloads, register moves/copies, `KeyInfo`, `FuncDef`, `CollSeq`, and scan-status annotations.
- SELECT/subquery integration flows through `sqlite3Select()`, `sqlite3SelectDup()`, `sqlite3SelectDelete()`, `sqlite3SelectDestInit()`, select flags such as `SF_Distinct`, `SF_Aggregate`, `SF_Correlated`, `SF_Values`, `SF_MultiValue`, and CTE/window duplication helpers.
- Table/index integration includes rowid aliases, WITHOUT ROWID primary-key column mapping, expression indexes, partial-index expressions, generated columns, virtual-table column reads, virtual-table function overloads, uniqueness/collation/affinity checks, and table locks/schema verification for `IN` RHS reuse.
- Function integration depends on the SQLite function registry and flags such as `SQLITE_FUNC_INLINE`, `SQLITE_FUNC_CONSTANT`, `SQLITE_FUNC_SLOCHNG`, `SQLITE_FUNC_DIRECT`, `SQLITE_FUNC_UNSAFE`, `SQLITE_FUNC_NEEDCOLL`, `SQLITE_FUNC_LENGTH`, `SQLITE_FUNC_TYPEOF`, and `SQLITE_RESULT_SUBTYPE`.
- Join and optimizer integration uses `EP_OuterON`, `EP_InnerON`, RIGHT/FULL join flags, single-table constraint checks, non-null-row implication, `IF_NULL_ROW` bytecode, and conservative proof helpers used by WHERE-clause planning.
- Feature macros alter behavior substantially, including `SQLITE_MAX_EXPR_DEPTH`, `SQLITE_OMIT_SUBQUERY`, `SQLITE_OMIT_FLOATING_POINT`, `SQLITE_OMIT_BLOB_LITERAL`, `SQLITE_OMIT_CAST`, `SQLITE_OMIT_WINDOWFUNC`, `SQLITE_OMIT_TRIGGER`, `SQLITE_OMIT_GENERATED_COLUMNS`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_ENABLE_CURSOR_HINTS`, `SQLITE_ENABLE_OFFSET_SQL_FUNC`, `SQLITE_ENABLE_UNKNOWN_SQL_FUNCTION`, `SQLITE_ENABLE_STMT_SCANSTATUS`, `SQLITE_ENABLE_COLUMN_USED_MASK`, and `SQLITE_ENABLE_SORTER_REFERENCES`.

## Risks And Edge Cases

- Expression deletion and duplication depend on compact-size flags, static buffers, token storage, `TK_SELECT_COLUMN` ownership exceptions, and window/list/select unions. Incorrect flag propagation can cause leaks, double frees, stale pointers, or missing subtree deletion.
- Reduced expression copies are only valid for pristine parser trees. Reusing reduced or analysis-mutated expressions in the reduction path would drop fields that later phases need.
- Collation and affinity selection affect query correctness, not just performance. `IN` index reuse is especially sensitive to matching affinity, collation, uniqueness, NULL behavior, and vector field ordering.
- `IN` and subquery subroutines cache bytecode in `Expr` fields and may be reused. Bugs in `SubrtnSig` matching, `EP_Subrtn` state, or `OP_Once` handling can cause stale RHS data, repeated work, or wrong results for correlated/variable-dependent expressions.
- The `IN` algorithm deliberately distinguishes FALSE from NULL only when required. Incorrect `destIfFalse`/`destIfNull` wiring or RHS NULL flag computation would break SQL three-valued logic.
- Boolean branch code assumes selected parser token values are identical to VDBE opcode values. Opcode renumbering or token changes must preserve the asserted relationships.
- Constant factoring can change when functions are evaluated. The code disables factoring around places where destination registers may be overwritten, where `OP_Affinity` mutates the LHS, or where functions may throw; missing such a guard can alter error timing or values.
- Generated-column evaluation uses `COLFLAG_BUSY` to catch loops and uses `iSelfTab` to resolve self references. Incorrect save/restore can misread row values or mask loops.
- Replacing expressions with expression-index columns is disabled when result subtypes might matter. Over-aggressive substitution can drop SQLite subtypes and change scalar-function behavior.
- Optimizer proof helpers intentionally accept false negatives but not false positives. Bugs in `sqlite3ExprImpliesExpr()`, `sqlite3ExprImpliesNonNullRow()`, or single-table constraint checks could incorrectly simplify joins, push predicates, or choose partial indexes.
- Aggregate analysis mutates expression nodes into `TK_AGG_COLUMN`/`TK_AGG_FUNCTION` references. Because this chunk ends mid-function case, merge/reconciliation with the next chunk is needed before drawing full conclusions about aggregate-function registration, DISTINCT handling, filters, or sorter column assignment.
- Variable-number assignment and parameter comparison interact with limits, reprepare masks, and QPSG. Off-by-one errors here can bind the wrong SQL parameter or miss needed reprepare.

## Test Signals

- Affinity/collation tests: comparisons involving column affinities, explicit and soft `COLLATE`, CAST, vector fields, function-deferred affinity, expression indexes with non-BINARY collations, and index eligibility via `sqlite3IndexAffinityOk()`.
- Expression lifetime tests: parser OOM paths, reduced schema-expression duplication, trigger/view/subquery duplication, window-function duplication, vector-update assignment ownership, `TK_SELECT_COLUMN` shared-select ownership, and rename-token cleanup.
- Constant/default tests: TRUE/FALSE identifiers, DEFAULT expressions from new DDL versus sqlite_schema, bound parameters in legacy schema text, deterministic/slow-changing functions, double-quoted strings, and expression-depth limits.
- `IN` tests: scalar and vector `IN`, empty lists, two-element lists using comparison fallback, NULL on LHS/RHS, rowid RHS, existing-index RHS with reordered columns, unique versus nonunique RHS, correlated subqueries, cloned RHS subqueries, Bloom-filter-enabled paths, and `NOT IN` false/null distinctions.
- Subquery tests: scalar SELECT column-count errors, EXISTS, correlated versus uncorrelated caching, LIMIT/OFFSET/DISTINCT interactions, subquery result initialization to NULL, reuse of coded subqueries, and select-codegen failure paths.
- Codegen tests: literals including oversized integer and hex literals, blobs, parameters, casts, arithmetic with subquery short-circuiting, COALESCE/IFNULL/iif inline behavior, function collation needs, DIRECTONLY/unsafe function restrictions in schema contexts, virtual-table function overloads, `length()`/`typeof()`/`octet_length()` column-load flags, CASE/BETWEEN common-subexpression reuse, and trigger `RAISE()`.
- Generated-column and column-read tests: REAL affinity on read, virtual generated columns in STRICT tables, generated-column loops, WITHOUT ROWID column mapping, virtual-table columns, rowid aliases in views if enabled, and default-value loading.
- Boolean jump tests: AND/OR/NOT short-circuiting, `IS`/`IS NOT`, `IS TRUE`/`IS FALSE`, vector comparisons, `BETWEEN` jump generation, `IN` jump generation, and NULL jump behavior.
- Optimizer proof tests: expression comparison with top-level COLLATE, bound variables during reprepare, expression implication for partial indexes, non-null-row implication for LEFT/RIGHT/FULL joins, virtual-table comparison exclusions, covering-index checks, and aggregate-source reference classification.
- Aggregate setup tests for the covered portion: duplicate aggregate columns, grouping-column sorter mapping, aggregate input expressions satisfied from expression indexes, `IF_NULL_ROW` aggregate columns, aggregate-term limit errors, OOM while growing `AggInfo`, and persistence of `AggInfo` expression pointers before later tree rewrites.

### subset-b-008770: lines 7507-7727

# sources/storage-engines/sqlite/src/expr.c lines 7507-7727

## Scope

This chunk covers the final part of `analyzeAggregate()`, the public aggregate-analysis wrappers, and the temporary VDBE register allocator helpers in `expr.c`. The aggregate-analysis code records aggregate functions, aggregate input columns, `DISTINCT`, and aggregate-local `ORDER BY` requirements in `AggInfo`. The register helpers manage reusable scratch registers in `Parse` while expression, SELECT, DML, pragma, analyze, where, and window code emits VDBE bytecode.

## Purpose

- Detect aggregate function expressions at the correct query nesting level and map each one to an `AggInfo.aFunc[]` entry.
- De-duplicate equivalent aggregate functions so later code generation shares accumulator state.
- Record implementation details for aggregate `DISTINCT` and aggregate `ORDER BY`, including ephemeral cursor allocation, payload layout, uniqueness handling, and subtype preservation.
- Expose `sqlite3ExprAnalyzeAggregates()` and `sqlite3ExprAnalyzeAggList()` as the post-name-resolution passes that populate `AggInfo` for individual expressions and expression lists.
- Provide small, centralized helpers for allocating, releasing, clearing, touching, and debug-validating temporary VDBE registers.
- Provide `sqlite3FirstAvailableRegister()` for STAT4/debug code that must find a scratch register range after all permanent constant-expression registers.

## Important APIs, Types, And Functions

- `analyzeAggregate()` is the walker callback that recognizes `TK_AGG_FUNCTION` nodes. This chunk handles the function case after column/index-expression handling from the preceding lines.
- `sqlite3ExprAnalyzeAggregates(NameContext *pNC, Expr *pExpr)` initializes a `Walker` with `analyzeAggregate`, select-depth callbacks, the current `NameContext`, and an assertion that `pNC->pSrcList` exists before walking one expression tree.
- `sqlite3ExprAnalyzeAggList(NameContext *pNC, ExprList *pList)` iterates an `ExprList` and calls `sqlite3ExprAnalyzeAggregates()` for each item.
- `AggInfo` is the SELECT aggregate descriptor. `aFunc[]` entries hold the aggregate expression, `FuncDef`, optional distinct cursor, optional aggregate-ordering cursor, and flags consumed by SELECT code generation.
- `AggInfo_func.iOBTab` is an ephemeral cursor number used when aggregate step calls must be deferred until inputs are sorted by an aggregate-local `ORDER BY`.
- `AggInfo_func.iDistinct` is an ephemeral cursor number used to enforce `DISTINCT` for aggregate arguments when uniqueness is not already handled by the aggregate-ordering key.
- `AggInfo_func.bOBPayload`, `bOBUnique`, and `bUseSubtype` describe the record layout and semantics of the aggregate `ORDER BY` sorter.
- `sqlite3GetTempReg()` and `sqlite3ReleaseTempReg()` allocate and release single scratch registers through `Parse.aTempReg[]`, falling back to new `Parse.nMem` cells when the cache is empty.
- `sqlite3GetTempRange()` and `sqlite3ReleaseTempRange()` allocate and release consecutive scratch register ranges through the single cached range described by `Parse.iRangeReg` and `Parse.nRangeReg`.
- `sqlite3ClearTempRegCache()` invalidates both scratch caches. Callers use it after coding subroutines or coroutines whose registers must not alias their callers.
- `sqlite3TouchRegister()` advances `Parse.nMem` so a manually chosen register number is considered allocated.
- `sqlite3FirstAvailableRegister()` is compiled for `SQLITE_ENABLE_STAT4` or `SQLITE_DEBUG`. It skips registers owned by `Parse.pConstExpr`, clears scratch caches, and returns a usable lower bound.
- `sqlite3NoTempsInRange()` is debug-only and asserts that neither cached scratch registers nor factored constant-expression registers overlap a protected range.

## Control Flow

For `TK_AGG_FUNCTION`, `analyzeAggregate()` only claims the node when the walker is not currently analyzing aggregate-function arguments, the walker depth matches the expression's recorded aggregate depth, and `pExpr->pAggInfo` has not already been set. This prevents inner or outer aggregate contexts from stealing each other's expressions and avoids recursive registration while `analyzeAggFuncArgs()` analyzes aggregate arguments.

The function first scans `pAggInfo->aFunc[]` for an equivalent aggregate expression using `sqlite3ExprCompare(..., -1)`. If a match is found, the current expression reuses that entry. If the index would exceed `SQLITE_LIMIT_COLUMN`, the parser records "more than %d aggregate terms" and clamps to the limit. Otherwise `addAggInfoFunc()` appends a new entry, `sqlite3FindFunction()` resolves the aggregate implementation for the database encoding and arity, and the entry is initialized.

Aggregate-local `ORDER BY` is represented by `pExpr->pLeft` with `TK_ORDER`. The code allocates a new VDBE cursor number from `pParse->nTab` when an order list exists and the aggregate function does not require collation through `SQLITE_FUNC_NEEDCOLL`; the comment notes that this ignores aggregate `ORDER BY` for `min()` and `max()`. If the order list is a single expression identical to the single aggregate argument, `bOBPayload` is false and `DISTINCT` can be enforced by unique ordering keys through `bOBUnique`. Otherwise the sorter needs payload columns. Subtype preservation is enabled only for functions with `SQLITE_SUBTYPE`.

After the ordering setup, the distinct path allocates another ephemeral cursor from `pParse->nTab` only when the aggregate has `EP_Distinct` and uniqueness was not already folded into the ordering cursor. The expression is marked `EP_NoReduce`, its `iAgg` index is set, `pExpr->pAggInfo` points back to the shared `AggInfo`, and the walker prunes the subtree because this aggregate node has been classified.

`sqlite3ExprAnalyzeAggregates()` is a thin walker setup. Its select callbacks increment and decrement `walkerDepth` so aggregate functions inside nested SELECTs are compared against the correct `Expr.op2` depth. `sqlite3ExprAnalyzeAggList()` provides the same analysis over result lists, `ORDER BY`, `GROUP BY`, `HAVING`, aggregate argument lists, and filter expressions used by callers in `select.c`.

The temporary-register helpers are intentionally simple. Single-register allocation pops the last cached value from `aTempReg[]` or creates a new cell by incrementing `nMem`. Releasing a non-zero register first tells the VDBE layer that the register is no longer live with `sqlite3VdbeReleaseRegisters()`, then caches it if the fixed-size holding area has room. Range allocation either consumes the front of the one cached range or appends `nReg` cells to `nMem`; range release records the released block only if it is larger than the existing cached block. Clearing resets both cache counts without changing `nMem`.

## State And Persistence Behavior

This chunk does not write database storage. It mutates parser-time structures that determine later bytecode:

- `AggInfo.aFunc[]` grows with aggregate function descriptors. `Expr.iAgg` and `Expr.pAggInfo` create reverse links from expression nodes to those descriptors.
- `AggInfo_func.pFunc` stores the `FuncDef` selected by name, arity, and database encoding.
- `AggInfo_func.iOBTab` and `iDistinct` reserve VDBE cursor numbers by incrementing `Parse.nTab`; later SELECT code opens ephemeral tables for these cursors.
- `AggInfo_func.bOBPayload`, `bOBUnique`, and `bUseSubtype` persist decisions needed by aggregate step/finalization bytecode, especially `ORDER BY` extraction and subtype propagation.
- `Expr` nodes are marked `EP_NoReduce` under VVA/debug property handling to prevent memory reduction from removing fields needed during aggregate code generation.
- `Parse.nMem` is the high-water mark for VDBE memory registers. The scratch helpers increase it but never shrink it.
- `Parse.aTempReg[]`, `nTempReg`, `iRangeReg`, and `nRangeReg` are compile-time caches only. They do not imply persistent VDBE state and may be invalidated by `sqlite3ClearTempRegCache()` or by `sqlite3FirstAvailableRegister()`.
- `Parse.pConstExpr` is treated as a set of permanent registers for factored constant expressions. The debug/STAT4 helper skips these when searching for available registers.

## Dependencies And Integration Points

- Name resolution must run before this pass; the comment explicitly limits `sqlite3ExprAnalyzeAggregates()` to expressions already processed by `sqlite3ResolveExprNames()`.
- The aggregate walker depends on `NameContext` flags such as `NC_UAggInfo` and `NC_InAggFunc`, `NameContext.uNC.pAggInfo`, `NameContext.pSrcList`, and `Parse.nErr`.
- `addAggInfoFunc()`, `findOrCreateAggInfoColumn()`, and `addAggInfoColumn()` from the surrounding code own `AggInfo` array growth and column mapping.
- `sqlite3ExprCompare()` is used both for aggregate-function de-duplication and for the aggregate-`ORDER BY` single-key/single-argument identity check.
- `sqlite3FindFunction()` resolves the function implementation and exposes flags such as `SQLITE_FUNC_NEEDCOLL` and `SQLITE_SUBTYPE`.
- SELECT aggregate code generation in `select.c` consumes the fields set here. `finalizeAggFunctions()` uses `iOBTab`, `bOBPayload`, `bOBUnique`, and `bUseSubtype` to replay sorted aggregate inputs before `OP_AggFinal`.
- `analyzeAggFuncArgs()` in `select.c` sets `NC_InAggFunc` and calls these wrappers on aggregate arguments, aggregate-local `ORDER BY` terms, and window aggregate filters.
- The register allocator is used broadly by expression evaluation, DML, WHERE-loop code, window functions, pragmas, `ANALYZE`, and SELECT output code. It integrates with `sqlite3VdbeReleaseRegisters()` so VDBE register lifetime metadata stays consistent.
- Debug callers such as `ANALYZE` use `sqlite3NoTempsInRange()` and `sqlite3FirstAvailableRegister()` to protect long-lived register ranges from accidental scratch-register reuse.

## Risks And Edge Cases

- The aggregate-function term-limit check uses `i>mxTerm`, while a new entry is added when `i>=pAggInfo->nFunc`. The surrounding assumptions that `mxTerm` fits in `i16` and existing entries remain valid are important because `Expr.iAgg` is a 16-bit field.
- Aggregate de-duplication depends on expression structural comparison. If comparison ignores or over-weights a semantic property, unrelated aggregate calls could share state or equivalent calls could get duplicate accumulators.
- The walker-depth and `NC_InAggFunc` gates are correctness boundaries for nested SELECTs and aggregate arguments. A regression here can attach expressions to the wrong aggregate context.
- Aggregate `ORDER BY` is deliberately ignored for functions with `SQLITE_FUNC_NEEDCOLL`, including `min()` and `max()` per the in-code comment. Tests should treat this as an intentional compatibility behavior, not missing sorter setup.
- The `bOBUnique` optimization is valid only when the single ordering expression exactly matches the single aggregate argument. Incorrectly enabling it would make the ordering table enforce distinctness on the wrong key.
- `pItem->pFunc` is assumed available after `sqlite3FindFunction()`; earlier resolution is expected to have rejected unknown aggregate functions. The assertion-style flow relies on that pipeline.
- Releasing the same temporary register twice, releasing a register still referenced by future bytecode, or clearing caches too late can cause subtle register aliasing in generated VDBE programs.
- `sqlite3ReleaseTempRange()` keeps only the largest returned range. Smaller returned ranges are intentionally discarded, so callers cannot assume every released block will be reused.
- `sqlite3TouchRegister()` only raises `nMem`; it does not remove overlapping scratch-cache entries. Callers that protect manually assigned ranges may need `sqlite3ClearTempRegCache()` or debug assertions.
- `sqlite3NoTempsInRange()` is debug-only. Release builds rely on callers following the scratch-register ownership protocol.

## Test Signals

- Aggregate queries should reuse duplicate aggregate expressions in generated plans/results while still producing correct answers for syntactically or semantically different aggregates.
- Nested aggregate contexts should be covered with subqueries in SELECT lists, HAVING clauses, aggregate arguments, and window filters to verify walker-depth handling.
- Aggregate `DISTINCT` should be tested with and without aggregate-local `ORDER BY`, especially the one-argument/one-order-key case where `bOBUnique` replaces a separate distinct table.
- Ordered aggregates such as `string_agg()`/`group_concat()` with one key, multiple keys, payload columns, duplicate inputs, and subtype-bearing values should exercise `iOBTab`, `bOBPayload`, and `bUseSubtype`.
- `min()` and `max()` with aggregate-local `ORDER BY` should preserve the documented behavior implied by the `SQLITE_FUNC_NEEDCOLL` exclusion.
- Limit tests should drive many aggregate terms to verify the `SQLITE_LIMIT_COLUMN` error path and that no out-of-range `Expr.iAgg` values are generated.
- OOM tests around `addAggInfoFunc()` and function analysis should leave `Parse.nErr`/malloc failure state consistent and avoid dereferencing missing `AggInfo` entries.
- Register-allocation tests are mostly indirect: expression-heavy SELECT, INSERT, UPDATE, WHERE, pragma, window, and ANALYZE tests should run under debug builds with `sqlite3NoTempsInRange()` assertions enabled.
- Subroutine and coroutine paths should continue to call `sqlite3ClearTempRegCache()` before reusable code can be invoked from multiple places, preventing scratch-register aliasing between caller and callee.
- STAT4/debug builds should cover `sqlite3FirstAvailableRegister()` with factored constant expressions so it skips `Parse.pConstExpr` registers before allocating analysis memory.
