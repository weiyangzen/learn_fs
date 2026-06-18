<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_rtree.c -->
# sources/storage-engines/sqlite/src/test_rtree.c

## Purpose
`test_rtree.c` registers test geometry and query callbacks for SQLite R-Tree modules. It validates both first-generation geometry callbacks and second-generation query callbacks with scoring and `eWithin` pruning behavior.

## Important APIs, Types, And Functions
Important types are `Circle` and `Cube`. Callback functions include `circle_geom()`, `circle_query_func()`, `bfs_query_func()`, and `cube_geom()`, with destructors for cached user data. Tcl registration commands are `register_circle_geom` and `register_cube_geom`, implemented by `register_circle_geom()` and `register_cube_geom()`, and the initializer is `Sqlitetestrtree_Init()`.

## Control Flow
For `circle`, the first invocation validates dimensions and parameters, allocates a cached `Circle`, derives center/radius and two helper boxes, then evaluates each R-Tree rectangle by corner inclusion and cross-box coverage. `Qcircle` supports either four numeric arguments or a single parsed string and sets scores for depth-first, breadth-first, leaf-area ordering, and odd-rowid exclusion cases. `breadthfirstsearch` compares candidate rectangles with a query rectangle and propagates `FULLY_WITHIN` from parents. `cube` validates six coordinates and checks 3D interval overlap.

## State And Persistence Behavior
Callback state is per-query and cached in `pUser`, then freed by `xDelUser`. There is no persistent storage beyond the R-Tree tables operated on by tests. `cube_geom()` asserts that the registered context pointer equals `&gHere`, making context delivery part of the test surface.

## Dependencies And Integration Points
The code is active only with `SQLITE_ENABLE_RTREE`. It uses SQLite's `sqlite3_rtree_geometry_callback()` and `sqlite3_rtree_query_callback()` APIs and Tcl's database-pointer helper. If R-Tree is omitted, registration commands are harmless stubs.

## Risks And Test Signals
Risks include floating-point boundary decisions, manual string parsing via `atof()`, returning `SQLITE_NOMEM` for a negative `Qcircle` radius after freeing cached memory, and tests depending on exact callback scoring order. Test signals include correct intersection results for circle and cube boundaries, parameter validation failures, destructor calls, query order changes for each score type, `FULLY_WITHIN` pruning, and omitted-build behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/src/test_rtree.c -->
