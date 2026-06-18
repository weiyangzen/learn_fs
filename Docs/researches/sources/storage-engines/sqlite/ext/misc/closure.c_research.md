# sources/storage-engines/sqlite/ext/misc/closure.c

## Purpose

`closure.c` implements the `transitive_closure` virtual table module. It computes descendants, ancestors, or other graph walks over an application table that stores integer child/parent relationships. A virtual table instance can define default `tablename`, `idcolumn`, and `parentcolumn` arguments, and queries can override those through hidden-column equality constraints.

## Important APIs, types, and functions

The public integration point is `sqlite3_closure_init()`, which registers module name `transitive_closure` unless virtual tables are omitted. `closureModule` provides create/connect, best-index, cursor open/close, filter, next/eof/column/rowid callbacks. `closure_vtab` stores the database handle, module table name, configured source table/columns, and cursor count. `closure_cursor` stores per-scan overrides plus `pClosure` and `pCurrent`.

The implementation uses `closure_avl` as both the visited set and sorted output tree. `closureAvlInsert()`, `closureAvlSearch()`, rotations, and balancing keep seen ids unique and sorted. `closure_queue` plus `queuePush()` and `queuePull()` drive breadth-first traversal by generation depth. `closureDequote()` and `closureValueOfKey()` parse module arguments such as `tablename='group'`.

## Control flow

`closureConnect()` parses module arguments, stores defaults, and declares `CREATE TABLE x(id,depth,root HIDDEN,tablename HIDDEN,idcolumn HIDDEN,parentcolumn HIDDEN)`. `closureBestIndex()` recognizes usable constraints on `root`, `depth`, `tablename`, `idcolumn`, and `parentcolumn`; if required table and column names or `root=?` are missing, it chooses a plan that returns no rows. It also consumes `ORDER BY id ASC` because AVL iteration is sorted by id.

`closureFilter()` clears the cursor, reads the root and optional max depth/table/column overrides from argv positions encoded in `idxNum`, prepares a child lookup query, inserts the root at generation 0, then repeatedly pulls queued nodes and queries rows whose parent column equals the current id. Integer child ids not already present in the AVL tree are inserted and queued with `generation+1`. When traversal finishes, `pCurrent` is set to the first AVL node. `closureNext()` advances by in-order AVL successor.

## State and persistence

The virtual table itself persists only its configured strings inside the SQLite connection. Query results are transient cursor state; no database writes occur. The source hierarchy table is read through a prepared `SELECT` with quoted identifiers. The traversal state is all in memory, with duplicate suppression by id.

## Dependencies and integration points

The extension depends on SQLite loadable extension APIs, virtual table APIs, `sqlite3_mprintf()` identifier quoting, and the source table having integer ids. The opening comments stress an index on the parent column for performance. The module is read-only and has no `xUpdate`.

## Risks

Runtime table and column names are accepted from SQL constraints, so correct quoting with `%w` is essential. Cycles are handled by the visited AVL tree, but very large closures can consume memory. Only integer child ids are followed; non-integer ids are silently ignored. `depth < N` is implemented by decrementing the max generation, so boundary tests matter. Missing root or metadata constraints intentionally produce empty output, which can hide query mistakes.

## Test signals

Useful tests create a small tree with an index on the parent column and verify root self inclusion, depth equality and inequality behavior, ancestor traversal by swapping id/parent columns, per-query overrides, sorted `ORDER BY id`, cycle suppression, empty output without root, and error propagation for bad table/column names.
