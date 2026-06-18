# sources/storage-engines/sqlite/ext/rtree/test_rtreedoc.c

## Purpose
`test_rtreedoc.c` is a Tcl test extension for exercising documented R-Tree callback APIs. It registers Tcl commands that install a legacy `box` geometry callback and a newer `qbox` query callback on a SQLite connection, then bridges callback invocations back into Tcl scripts for validation.

## Important APIs, Types, And Functions
`BoxGeomCtx` and `BoxQueryCtx` hold `Tcl_Interp*` plus a retained Tcl script object. `testDelUser()` exercises `sqlite3_rtree_geometry.pUser` cleanup by evaluating a saved Tcl script and freeing the context.

`invokeTclGeomCb()` constructs the Tcl callback invocation for legacy geometry callbacks. It passes the callback name, registration context pointer, parameter list, coordinate list, and geometry object pointer. It also interprets Tcl result commands such as `zero`, `user`, and `user_is_zero` to mutate or validate `sqlite3_rtree_geometry` state.

`box_geom()` is the legacy R-Tree geometry callback registered as SQL function `box`. It verifies parameter count, invokes Tcl, checks rectangle overlap against the supplied bounds, and writes the match result through `pRes`.

`register_box_geom` is the Tcl command that resolves a SQLite connection pointer, allocates a geometry context, registers `box` with `sqlite3_rtree_geometry_callback()`, and returns the context pointer string.

`box_query()` is the newer query callback registered as SQL function `qbox`. It builds a Tcl dictionary/list-like argument containing `aParam`, `aCoord`, `anQueue`, `iLevel`, `mxLevel`, `iRowid`, `rParentScore`, and textual `eParentWithin`, evaluates the script, and expects a two-element result containing visibility and score.

`box_query_destroy()` releases query callback script state, and `register_box_query` installs the query callback through `sqlite3_rtree_query_callback()`. `Sqlitetestrtreedoc_Init()` registers the two Tcl commands when R-Tree is enabled.

## Control Flow
The test extension initializes via `Sqlitetestrtreedoc_Init()`. Tcl test scripts call `register_box_geom DB SCRIPT` or `register_box_query DB SCRIPT`. Those commands capture the script and register an SQL callback function on the target database connection.

When SQL executes an R-Tree `MATCH box(...)` constraint, `rtree.c` invokes `box_geom()`. The callback forwards observable state to Tcl, optionally lets Tcl mutate callback-owned user state, then performs deterministic bounding-box overlap logic and returns a match flag.

For `MATCH qbox(...)`, `rtree.c` invokes `box_query()` for internal nodes and leaf entries. The callback forwards traversal state to Tcl and uses the Tcl result to set `pInfo->eParentWithin` and `pInfo->rScore`, allowing tests to validate scored traversal behavior and queue visibility.

## State And Persistence Behavior
The file owns only test callback state. Tcl scripts are reference-counted and freed through explicit destructor paths. Legacy geometry callbacks can allocate per-query `pUser` state via Tcl result handling; that state is later cleaned through `testDelUser()`.

No database state is persisted directly by this file. Its SQL callback registration affects only the SQLite connection used by tests.

## Dependencies
The file depends on `sqlite3.h`, `tclsqlite.h`, Tcl object APIs, and `sqliteInt.h` for `UNUSED_PARAMETER()`. It is compiled only when `SQLITE_ENABLE_RTREE` code paths are relevant; command registration is guarded accordingly.

## Integration Points
This is a test harness for `sqlite3rtree.h` and `rtree.c`. It validates documented evidence comments around legacy callback arguments and exposes internal callback fields to Tcl test scripts without adding production APIs.

## Risks And Edge Cases
There is a likely allocation-size bug in `register_box_geom`: it uses `ckalloc(sizeof(BoxGeomCtx*))` instead of `sizeof(BoxGeomCtx)`, which allocates pointer size rather than structure size. On platforms where the structure is larger than a pointer, this can corrupt memory in tests.

Callback return parsing is strict. `box_query()` expects exactly two Tcl result elements, a visibility token from `not`, `partly`, or `fully`, and a double score. Script errors propagate as `SQLITE_ERROR`. Pointer strings are used only for test visibility and should not be treated as stable external identifiers.

## Test Signals
Tests should verify legacy callback argument count and contents, rectangle match decisions, `pUser` allocation and destructor behavior, query callback traversal fields, queue counts, rowid visibility on leaf entries, score ordering, and error propagation from Tcl scripts. Memory sanitizer coverage is useful because this file crosses Tcl, SQLite, and manually allocated context objects.
