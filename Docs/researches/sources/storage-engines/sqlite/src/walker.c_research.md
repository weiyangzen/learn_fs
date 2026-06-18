# sources/storage-engines/sqlite/src/walker.c

## Purpose

`walker.c` implements SQLite's generic parse-tree walker for SQL expressions and `SELECT` statements. It centralizes traversal order and callback dispatch so semantic analysis, name resolution, aggregate/window processing, rewrite passes, and validation code can inspect or transform parse trees without duplicating recursion logic.

## Important APIs, Types, and Functions

The file operates on the `Walker` type declared in `sqliteInt.h`. A `Walker` supplies `xExprCallback`, `xSelectCallback`, optional `xSelectCallback2`, parser context, and depth bookkeeping. Callback return values are `WRC_Continue`, `WRC_Prune`, and `WRC_Abort`.

`sqlite3WalkExprNN()` is the non-null expression walker. It invokes `xExprCallback()` before children, prunes children if the callback returns `WRC_Prune`, aborts on `WRC_Abort`, and otherwise descends into left/right children, subqueries, expression lists, and window-function metadata. `sqlite3WalkExpr()` is the null-safe wrapper. `sqlite3WalkExprList()` walks every expression in an `ExprList`.

`sqlite3WalkSelectExpr()` walks expressions attached to a `Select`: result list, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT, and conditionally window definitions. `sqlite3WalkSelectFrom()` walks subqueries and table-function arguments in the FROM clause. `sqlite3WalkSelect()` performs full SELECT traversal: pre-order select callback, expressions, FROM subqueries, optional post-order callback, and then the compound-select `pPrior` chain.

Window support is compiled unless `SQLITE_OMIT_WINDOWFUNC` is set. The private `walkWindowList()` walks ORDER BY, PARTITION BY, FILTER, frame start, and frame end expressions for a linked list of `Window` objects. `sqlite3WalkWinDefnDummyCallback()` is a no-op marker callback that causes `sqlite3WalkSelectExpr()` to traverse `Select.pWinDefn`.

Utility callbacks include `sqlite3WalkerDepthIncrease()`, `sqlite3WalkerDepthDecrease()`, `sqlite3ExprWalkNoop()`, and `sqlite3SelectWalkNoop()`.

## Control Flow

Expression traversal is pre-order. `sqlite3WalkExprNN()` calls the expression callback first; a nonzero callback result is masked with `WRC_Abort`, meaning `WRC_Prune` stops descent into that expression's children but lets sibling traversal continue. The function avoids recursion on the right child by tail-recursing through a loop when `pRight` exists. It asserts that an expression uses either `x.pList` or `pRight`, not both, and does not descend into token-only or leaf expressions.

Select traversal is also pre-order for the select callback. If no `xSelectCallback` is configured, `sqlite3WalkSelect()` is a no-op. Otherwise, for each select in the compound chain, it invokes `xSelectCallback()`, walks local expressions and FROM subqueries, then invokes `xSelectCallback2()` if present. `sqlite3WalkSelectExpr()` deliberately does not invoke the select callback for the current select; it only walks expressions and may walk window definitions when the callback state indicates rename processing, WITH-pop cleanup, or explicit window-definition traversal.

FROM traversal visits subquery SELECTs recursively and table-function argument expression lists. Compound SELECT traversal proceeds through `pPrior` after each current select is processed.

## State and Persistence Behavior

`walker.c` does not persist data and performs no I/O. Its only direct state mutation is through callbacks and `Walker.walkerDepth`. `sqlite3WalkerDepthIncrease()` increments depth on subquery entry and `sqlite3WalkerDepthDecrease()` decrements it on exit. The generic walker may indirectly mutate parse-tree nodes if caller-provided callbacks do so.

Because callbacks can abort, prune, or mutate, traversal state is intentionally simple and synchronous. Return values propagate `WRC_Abort` upward immediately to stop the full walk.

## Dependencies and Integration Points

The file depends on `sqliteInt.h` for all parse-tree types and macros, plus standard headers. It is integrated with expression structures (`Expr`, `ExprList`), SELECT structures (`Select`, `SrcList`, `SrcItem`), subquery wrappers, table-valued function arguments, window definitions, parser rename state (`IN_RENAME_OBJECT`), and CTE cleanup (`sqlite3SelectPopWith`) when CTE support is compiled.

Many SQLite subsystems use these traversal APIs indirectly through prototypes in `sqliteInt.h`. The walker provides consistent traversal semantics for name resolution, aggregate analysis, window handling, expression rewriting, authorization checks, and other parse-analysis passes.

## Risks and Edge Cases

The walker assumes parse-tree invariants such as non-null input to `sqlite3WalkExprNN()`, no simultaneous `x.pList` and `pRight`, and valid `SrcList` for a `Select`. Callers must use `sqlite3WalkExpr()` for nullable expressions. A callback returning the wrong `WRC_*` value can accidentally abort traversal or skip required children.

Window-definition traversal is intentionally conditional. A new caller that needs `pWinDefn` walked must use the recognized callback setup or update this logic. The `rc & WRC_Abort` masking behavior is subtle but important: `WRC_Prune` is returned as continue from the top-level walk after children are skipped. Changes here could break many semantic passes.

Deep parse trees still recurse through left children, expression lists, subqueries, and SELECT chains, so stack depth remains a consideration even with the right-child loop optimization. Mutating callbacks must account for traversal order and avoid invalidating nodes that the walker will visit later.

## Test Signals

Tests should cover expression callbacks that continue, prune, and abort; null expressions and empty expression lists; left/right expression trees; subquery expressions; FROM-clause subqueries; table-valued function arguments; compound SELECT chains; post-order select callbacks; window-function expressions and named window definitions; rename-object traversal; and walker-depth increment/decrement pairing.

Regression signals include name-resolution tests, aggregate/window query tests, ALTER TABLE rename tests, CTE tests, and parser fuzzing. Sanitizer or debug builds should catch invariant violations in malformed or transformed parse trees.
