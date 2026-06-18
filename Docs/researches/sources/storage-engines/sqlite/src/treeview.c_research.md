# sources/storage-engines/sqlite/src/treeview.c

## Purpose

`treeview.c` implements SQLite debug-only parse-tree and AST printers. Under `SQLITE_DEBUG`, it formats internal structures such as columns, WITH clauses, source lists, SELECTs, window definitions, expressions, expression/id lists, upserts, DML statements, trigger steps, and triggers as an ASCII tree on stdout. It also exposes `sqlite3Show*()` helper functions intended for interactive debuggers.

## Important APIs, Types, And Functions

- `sqlite3TreeViewPush()`, `sqlite3TreeViewPop()`, `sqlite3TreeViewLine()`, and `sqlite3TreeViewItem()` manage indentation state and line output.
- `sqlite3TreeViewColumnList()`, `sqlite3TreeViewWith()`, `sqlite3TreeViewSrcList()`, and `sqlite3TreeViewSelect()` print schema/query structures.
- `sqlite3TreeViewBound()`, `sqlite3TreeViewWindow()`, and `sqlite3TreeViewWinFunc()` print window frame and function structures when window functions are enabled.
- `sqlite3TreeViewExpr()` is the central expression-node formatter and handles many token opcodes and expression flags.
- `sqlite3TreeViewBareExprList()`, `sqlite3TreeViewExprList()`, `sqlite3TreeViewBareIdList()`, and `sqlite3TreeViewIdList()` print list structures.
- `sqlite3TreeViewUpsert()`, and `TREETRACE_ENABLED` DML printers (`sqlite3TreeViewDelete()`, `sqlite3TreeViewInsert()`, `sqlite3TreeViewUpdate()`) show higher-level statement inputs.
- `sqlite3TreeViewTriggerStep()` and `sqlite3TreeViewTrigger()` print trigger structures.
- `sqlite3ShowExpr()`, `sqlite3ShowSelect()`, `sqlite3ShowTrigger()`, and related wrappers provide debugger-friendly entry points.

## Control Flow

Printer calls push a tree level, emit a line with prefix characters based on `TreeView.bLine[]`, recursively print child structures, then pop the level. Passing a null `TreeView *` to top-level routines lazily allocates a view on first push and frees it after the final pop.

`sqlite3TreeViewSelect()` prints WITH, result set, window functions, FROM, WHERE, GROUP BY, HAVING, WINDOW definitions, ORDER BY, LIMIT/OFFSET, and compound SELECT links. `sqlite3TreeViewExpr()` switches on expression opcode to print literals, columns, functions, aggregates, subqueries, IN/BETWEEN/CASE, trigger references, vectors, collations, truth operators, and binary/unary operators, recursing into children and lists as needed.

The DML and trigger printers are compiled only when their feature macros are enabled. Debugger wrappers omit many parameters and print a complete tree for a single object.

## State And Persistence Behavior

The module does not alter persistent database state. It allocates transient `TreeView` objects and temporary formatted strings, writes to stdout, and flushes after output. It inspects internal AST flags, pointers, cursor numbers, and schema metadata but should not mutate them.

## Dependencies And Integration Points

The file depends on `sqliteInt.h`, internal AST structs (`Select`, `Expr`, `SrcList`, `Window`, `Trigger`, `Upsert`, etc.), `sqlite3_str`/`StrAccum` formatting helpers, debug feature macros, and stdout. It integrates with tree-tracing code and debugger workflows across parser, resolver, planner, trigger, and window-function development.

## Risks And Edge Cases

- It is debug-only but often used while diagnosing parser/planner bugs; stale formatting can mislead debugging.
- The code dereferences many internal unions and flag-dependent fields, so it must stay synchronized with AST layout invariants such as `ExprUseXList()` and `ExprUseXSelect()`.
- Output includes raw pointers and flags; this is useful for debugging but unsuitable as stable test output across processes.
- Fixed-size buffers are used for lines, relying on SQLite string accumulators to avoid overflow.
- Very deep trees are truncated visually by the fixed `bLine` depth array, though recursion still proceeds.

## Test Signals

Signals are mostly debug-build checks: compile with `SQLITE_DEBUG`, call `sqlite3Show*()` from targeted tests or debugger sessions, and verify no assertions for representative SELECTs, joins, CTEs, expressions, window frames, triggers, upserts, and DML tree traces. Golden-output tests should avoid pointer values or mask them.
