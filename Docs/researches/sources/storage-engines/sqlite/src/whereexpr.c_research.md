# sources/storage-engines/sqlite/src/whereexpr.c

## Purpose

`whereexpr.c` analyzes SQL expression trees for the WHERE planner. It turns raw `Expr` trees into `WhereClause`/`WhereTerm` records with operator masks, prerequisite masks, cursor/column bindings, virtual terms, OR/AND subclauses, virtual-table auxiliary constraints, LIMIT/OFFSET constraints, and table-valued-function argument constraints.

This file does not choose final plans or emit most loop bytecode. Its output is the normalized and annotated term set consumed by planner enumeration and by `wherecode.c`.

## Important APIs and functions

WHERE-clause lifecycle:

- `sqlite3WhereClauseInit()` initializes a `WhereClause` with static term storage.
- `sqlite3WhereSplit()` recursively splits an expression tree by `AND` or `OR` into `WhereTerm` slots.
- `sqlite3WhereExprAnalyze()` walks base terms from end to beginning and calls `exprAnalyze()`; this ordering prevents newly appended virtual terms from being processed as base terms.
- `sqlite3WhereClauseClear()` frees dynamic expressions and nested `WhereOrInfo`/`WhereAndInfo` clauses.

Term insertion and normalization:

- `whereClauseInsert()` appends a term, grows storage with `sqlite3WhereMalloc()`, initializes truth probability from `EP_Unlikely`, and updates `nBase` for non-virtual terms.
- `allowedOp()` and `operatorMask()` identify operators that can become `WO_*` planner constraints.
- `exprCommute()` swaps comparison sides and fixes operator direction while preserving collation/vector semantics through `EP_Commuted`.
- `termIsEquivalence()` decides whether a column-column equality/IS term can be used for transitive substitution.
- `exprMightBeIndexed()` and `exprMightBeIndexed2()` determine whether an operand is a table column or expression-index candidate.

Derived/virtual-term analysis:

- `exprAnalyze()` is the main analyzer. It computes prerequisite masks, identifies left cursor/column, creates commuted terms, creates BETWEEN bounds, analyzes OR clauses, rewrites `IS NOT NULL`, adds LIKE/GLOB range terms, splits vector equality, slices vector IN, adds virtual-table auxiliary terms, and adjusts outer-join prerequisites.
- `exprAnalyzeOrTerm()` decomposes OR terms into `WhereOrInfo`, detects OR-to-IN transformations, recognizes indexable OR branches, creates nested `WhereAndInfo`, and creates helper conjuncts such as `x>=A` from `x>A OR (x=A AND ...)`.
- `whereCombineDisjuncts()` creates compatible virtual conjuncts from two OR branches.
- `markTermAsChild()` and `transferJoinMarkings()` preserve parent/child disabling behavior and outer-join ON markings.
- `whereNthSubterm()` iterates nested AND subterms under OR analysis.

LIKE, virtual-table, and usage helpers:

- `isLikeOrGlob()` detects optimizable LIKE/GLOB prefixes, including bound-parameter reprepare handling, escape removal, UTF-8 safety, numeric-prefix hazards, and collation/case decisions.
- `sqlite3ExprIsLikeOperator()` maps `match`, `glob`, `like`, and `regexp` function names to virtual-table constraint codes.
- `isAuxiliaryVtabOperator()` recognizes virtual-table-only constraints such as MATCH/LIKE/GLOB/REGEXP, `!=`, `IS NOT`, and `NOT NULL`.
- `sqlite3WhereExprUsage()`, `sqlite3WhereExprUsageNN()`, `sqlite3WhereExprListUsage()`, and `sqlite3WhereExprUsageFull()` compute dependency bitmasks for expressions, subqueries, lists, table functions, and window-function components.
- `sqlite3WhereAddLimit()` and `whereAddLimitExpr()` add LIMIT/OFFSET pseudo-constraints for eligible single-virtual-table SELECTs.
- `sqlite3WhereTabFuncArgs()` converts table-valued-function arguments into equality terms against hidden columns.

## Control flow

The typical flow is:

1. `sqlite3WhereClauseInit()` prepares a `WhereClause`.
2. `sqlite3WhereSplit()` fills it with pointers into the original WHERE expression, split on `AND` for the top-level clause or `OR` for OR subclauses.
3. `sqlite3WhereTabFuncArgs()` may append hidden-column equality terms for table-valued functions.
4. `sqlite3WhereExprAnalyze()` calls `exprAnalyze()` for each base term.
5. `exprAnalyze()` computes `prereqLeft`, `prereqRight`, and `prereqAll`, adjusts for outer-join markings, and then applies specialized transformations:
   - Ordinary indexable comparisons get `leftCursor`, `leftColumn`, and `eOperator`.
   - If both sides are indexable, a commuted virtual term is appended and linked as a child.
   - BETWEEN becomes two virtual range terms.
   - OR terms are recursively split and analyzed into `WhereOrInfo`, possibly also producing IN or range-helper virtual terms.
   - `x IS NOT NULL` on ordinary columns can produce a virtual `x>NULL` range term tagged `TERM_VNULL`.
   - LIKE/GLOB prefix patterns produce lower and upper range terms tagged `TERM_LIKEOPT`.
   - Vector equality produces per-field slice terms and disables the original row-value term.
   - Vector IN with eligible SELECT RHS produces per-field virtual slices that share the original expression and use `u.x.iField`.
   - Virtual-table-only operators produce `WO_AUX` terms with `eMatchOp`.
6. Later planner code reads these terms to build loops, and `wherecode.c` may mark terms `TERM_CODED` when constraints are implemented.
7. `sqlite3WhereClauseClear()` recursively releases owned dynamic expressions and subclauses at teardown.

OR analysis has its own nested flow. `exprAnalyzeOrTerm()` first builds a `WhereOrInfo.wc`, analyzes all OR branches, tracks which tables are indexable, optionally builds nested `WhereAndInfo` clauses, marks the parent term `WO_OR`, tries two-way disjunct combination, and then tries OR-to-IN conversion when all equality branches share the same table column or compatible expression-index operand.

## State and persistence behavior

All state is compile-time planning state for a prepared statement:

- `WhereClause.a[]` may grow from static storage to `sqlite3WhereMalloc()`-managed storage owned by `WhereInfo`.
- Dynamic `Expr` copies are owned by terms tagged `TERM_DYNAMIC`.
- Nested OR/AND analysis allocates `WhereOrInfo`/`WhereAndInfo`, recursively containing `WhereClause` instances.
- `WhereTerm` fields are populated with dependencies, operator masks, child counts, parent indexes, truth probability, cursor/column ids, and special flags such as `TERM_VARSELECT`, `TERM_COPIED`, `TERM_VIRTUAL`, `TERM_SLICE`, `TERM_LIKE`, `TERM_LIKEOPT`, `TERM_VNULL`, `TERM_IS`, and `TERM_ORINFO`.
- Bound LIKE parameters mark VDBE variable masks to force reprepare when the pattern changes.
- Table-valued-function arguments and LIMIT/OFFSET pushdown append synthetic terms but do not change database state.

No database file state is persisted. The analyzed term structures live only for the statement compilation and are later encoded into a plan and VDBE program by other WHERE subsystem code.

## Dependencies and integration points

This file sits between parser expression trees and WHERE planner internals:

- Input expression structures come from `sqliteInt.h`: `Expr`, `ExprList`, `Select`, `SrcList`, `SrcItem`, `Table`, `Index`, join flags, expression flags, token codes, affinity/collation helpers, and virtual-table metadata.
- Output structures and flags come from `whereInt.h`: `WhereClause`, `WhereTerm`, `WhereOrInfo`, `WhereAndInfo`, `WhereMaskSet`, `WO_*`, `TERM_*`.
- Planner integration relies on `sqlite3WhereGetMask()` to translate cursor ids into bitmask dependencies and on `WhereTerm` fields consumed by loop builders.
- Codegen integration relies on `TERM_DYNAMIC`, parent-child relationships, `TERM_LIKECOND`, `TERM_SLICE`, `u.x.iField`, `WO_AUX`, and `eMatchOp`.
- Virtual-table integration uses `sqlite3ExprIsLikeOperator()`, `isAuxiliaryVtabOperator()`, hidden-column table-function terms, and LIMIT/OFFSET pseudo-constraints so `xBestIndex` can see nonstandard constraints.
- LIKE/GLOB optimization integrates with VDBE reprepare machinery for bound parameters and with `wherecode.c` two-pass LIKE/BLOB logic.
- Window-function and subquery usage analysis affects term scheduling because correlated subqueries are delayed in `wherecode.c`.

## Risks and edge cases

- `whereClauseInsert()` warns that term-array reallocation invalidates existing `WhereTerm *` pointers. Callers must reacquire pointers after inserting virtual terms.
- Outer-join markings are correctness-critical. `extraRight`, `EP_OuterON`, `EP_InnerON`, and `w.iJoin` prevent ON-clause terms from driving indexes on the wrong side of LEFT/RIGHT joins.
- OR-to-IN and transitive equivalence must respect affinity, collation, expression indexes, commuted expressions, and right joins. Incorrect `WO_EQUIV` can produce wrong answers.
- LIKE/GLOB prefix optimization has many hazards: UTF-8 malformed input, escape characters, numeric-looking prefixes on non-TEXT affinity, case folding, EBCDIC builds, bound parameters, and patterns that appear complete but still require runtime LIKE checks.
- Vector comparison slicing must not overrun child counters; the code explicitly guards vector IN child count against a 2026-06-04 bug. Row-value slices also must not be pushed into OR branches where RHS initialization might not run.
- `IS NOT NULL` to `x>NULL` is only safe for non-IPK ordinary columns and not for outer-join ON terms.
- Virtual-table auxiliary terms must avoid constraints where the RHS depends on the same table as the LHS.
- LIMIT/OFFSET pushdown is intentionally narrow. It is disabled for aggregate, DISTINCT, multi-source, unsupported ORDER BY, big-null ordering, and WHERE terms not fully passable to the virtual table.
- Usage-mask recursion through subqueries, table functions, and window expressions controls dependency scheduling. Missing a dependency can evaluate a term too early.

## Test signals

Regression coverage should include:

- Basic indexable terms for `=`, `<`, `<=`, `>`, `>=`, `IN`, `IS`, and `IS NULL`, including commuted forms.
- Column-column equality with transitive optimization on/off, mixed affinity, explicit collations, expression indexes, and RIGHT JOIN queries.
- BETWEEN expansion and parent-child disabling behavior.
- OR optimization cases: OR-to-IN, multi-index OR, nested AND branches, two-way disjunct range combination, expression-index OR terms, and OR terms with subqueries or row-value slices.
- LIKE/GLOB prefix optimization with bound parameters, escapes, non-ASCII, malformed UTF-8, numeric-looking prefixes, TEXT vs non-TEXT affinity, `NOCASE`, and BLOB-matching builds.
- Vector equality and vector IN with simple SELECT, VALUES, compound SELECT, window functions, large vectors, and OOM/fault injection.
- Virtual-table constraints for MATCH, LIKE, GLOB, REGEXP, `!=`, `IS NOT`, `NOT NULL`, overloaded functions, LIMIT/OFFSET, table-valued-function hidden columns, and omitted OFFSET.
- Outer join ON/WHERE combinations for LEFT, RIGHT, and JT_LTORJ joins, especially terms that would be legal inner-join pushdowns but illegal outer-join pushdowns.
- `WhereClauseClear()` under nested OR/AND and failed allocations to verify ownership and cleanup paths.
