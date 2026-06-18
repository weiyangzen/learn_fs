# sources/storage-engines/sqlite/ext/rtree/sqlite3rtree.h

## Purpose
`sqlite3rtree.h` is the public API header for application-defined R-Tree geometry and query callbacks. It lets embedders register SQL functions usable on the right side of R-Tree `MATCH` constraints.

## Important APIs, Types, And Functions
The header declares opaque/structured callback types `sqlite3_rtree_geometry` and `sqlite3_rtree_query_info`, and the coordinate scalar typedef `sqlite3_rtree_dbl`. `sqlite3_rtree_dbl` is `sqlite3_int64` when `SQLITE_RTREE_INT_ONLY` is defined and `double` otherwise.

`sqlite3_rtree_geometry_callback()` registers a legacy geometry callback. The callback receives an `sqlite3_rtree_geometry*`, coordinate count, coordinate array, and output integer indicating whether the candidate matches.

`sqlite3_rtree_query_callback()` registers the newer scored query callback. Its callback receives `sqlite3_rtree_query_info*` and can set `eWithin` and `rScore`, allowing priority-queue traversal and more expressive pruning/scoring.

`sqlite3_rtree_geometry` contains the registration context, numeric SQL parameters, and callback-owned `pUser` plus `xDelUser` cleanup hook. `sqlite3_rtree_query_info` begins with the same fields, then adds candidate coordinates, per-level queue counts, current level, max level, rowid, parent score/visibility, output score/visibility, and original SQL parameter values.

The visibility constants are `NOT_WITHIN`, `PARTLY_WITHIN`, and `FULLY_WITHIN`.

## Control Flow
Applications register a callback name against a connection. SQL then uses `WHERE coordinate_column MATCH callback_name(args...)`. The registered SQL scalar function packages callback metadata and SQL arguments into an internal typed pointer. During virtual-table filtering, `rtree.c` deserializes that pointer and invokes the callback for candidate internal nodes and leaf entries.

Legacy geometry callbacks return a boolean-like result through `*pRes`. Query callbacks can influence traversal order by writing `rScore` and can prune by writing `eWithin`. `iLevel`, `mxLevel`, `iRowid`, `rParentScore`, `eParentWithin`, and `anQueue` expose traversal context.

## State And Persistence Behavior
The header defines transient callback state only. `pContext` is the registration-time application pointer. `pUser` is per-query mutable callback state and may be cleaned with `xDelUser`. No persistent R-Tree shadow table state is defined here.

## Dependencies
The header depends on `<sqlite3.h>` and C linkage support for C++. Its ABI must match the implementation in `rtree.c`, especially the shared first fields of `sqlite3_rtree_geometry` and `sqlite3_rtree_query_info`.

## Integration Points
This is the application-facing counterpart to `rtree.c` callback plumbing and to the Tcl tests in `test_rtreedoc.c`. Extensions and applications include it when they want custom spatial predicates or nearest-neighbor-like scoring behavior.

## Risks And Edge Cases
Callback implementations must treat `aCoord` as read-only candidate bounds and must set output fields consistently. Returning invalid `eWithin` values, negative or unordered scores, or retaining pointers beyond their lifetime can break query behavior. The `apSqlParam` field is available only in newer SQLite versions according to the header comment, so external code should account for version compatibility.

`sqlite3_rtree_dbl` changes type under `SQLITE_RTREE_INT_ONLY`; callback code compiled with mismatched settings can misinterpret coordinates and parameters.

## Test Signals
Tests should register both callback generations, invoke them with different parameter counts and types, confirm `pContext` and `pUser` cleanup, verify callback pruning and scoring, and cover integer-only builds. ABI tests should verify C++ inclusion and that the first fields of `sqlite3_rtree_query_info` remain compatible with `sqlite3_rtree_geometry`.
