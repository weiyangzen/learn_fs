# sources/storage-engines/sqlite/ext/rtree/rtree.c

## Purpose
`rtree.c` implements SQLite's R-Tree and R*-Tree virtual table modules. It exposes SQL modules named `rtree` and `rtree_i32`, supports optional auxiliary columns, stores spatial index state in SQLite shadow tables, and provides read, write, rename, transaction, integrity-check, and loadable-extension entry points.

The file owns the full on-disk node format for R-Tree tables. Each virtual table maps to `%_node`, `%_parent`, and `%_rowid` shadow tables. `%_node` stores fixed-size node blobs, `%_parent` maps child node numbers to parent node numbers, and `%_rowid` maps user rowids to leaf node numbers plus auxiliary column values. Node 1 is always the root and stores tree depth in its first two bytes.

## Important APIs, Types, And Functions
`sqlite3RtreeInit(sqlite3 *db)` registers helper SQL functions `rtreenode()`, `rtreedepth()`, `rtreecheck()`, the `rtree` module, and the integer-coordinate `rtree_i32` module. Loadable builds expose `sqlite3_rtree_init()`.

The public callback APIs implemented here are `sqlite3_rtree_geometry_callback()` and `sqlite3_rtree_query_callback()`. They register SQL scalar functions whose result is a typed `RtreeMatchArg` pointer consumed by `MATCH` constraints during R-Tree scans.

Core state types are `Rtree`, `RtreeCursor`, `RtreeNode`, `RtreeCell`, `RtreeConstraint`, `RtreeSearchPoint`, `RtreeGeomCallback`, and `RtreeMatchArg`. `Rtree` owns module metadata, node size, coordinate mode, prepared statements for shadow tables, a reusable blob handle for `%_node`, a small in-memory node hash, and transaction/cursor counters. `RtreeCursor` owns scan constraints, a priority queue of `RtreeSearchPoint` objects, a small node cache, and lazy auxiliary-column state.

The SQLite virtual-table module table wires `xCreate/xConnect` to `rtreeInit()`, planning to `rtreeBestIndex()`, scanning to `rtreeFilter()`, `rtreeNext()`, `rtreeColumn()`, `rtreeRowid()`, mutation to `rtreeUpdate()`, lifecycle to `rtreeDisconnect()`/`rtreeDestroy()`, transaction hooks to `rtreeBeginTransaction()`/`rtreeEndTransaction()`/`rtreeRollback()`, rename to `rtreeRename()`, shadow-table recognition to `rtreeShadowName()`, and integrity checking to `rtreeIntegrity()`.

Low-level node IO is handled by `readInt16()`, `readCoord()`, `readInt64()`, `writeInt16()`, `writeCoord()`, `writeInt64()`, `nodeAcquire()`, `nodeWrite()`, `nodeRelease()`, `nodeInsertCell()`, `nodeDeleteCell()`, and `nodeOverwriteCell()`. Tree algorithms include `ChooseLeaf()`, `AdjustTree()`, `splitNodeStartree()`, `SplitNode()`, `deleteCell()`, `removeNode()`, `fixBoundingBox()`, `reinsertNodeContent()`, `rtreeInsertCell()`, and `rtreeDeleteRowid()`.

## Control Flow
Creation and connection enter `rtreeInit()`. It validates constructor arguments, separates coordinate columns from optional `+aux` columns, declares the virtual table schema, calculates dimension count and cell size, obtains node size with `getNodeSize()`, and calls `rtreeSqlInit()` to create or prepare shadow-table SQL. `rtreeSqlInit()` creates `%_rowid`, `%_node`, `%_parent`, inserts the root zeroblob when creating, prepares persistent statements, and prepares auxiliary-column read/write SQL if needed.

Planning in `rtreeBestIndex()` recognizes two strategies. Strategy 1 is a direct rowid lookup when there is a usable equality constraint on rowid and no `MATCH` constraint. Strategy 2 is an R-Tree scan using coordinate comparisons or callback `MATCH` constraints encoded into a two-byte-per-constraint `idxStr`. Cost is based on `sqlite_stat1` row estimates when available.

Query execution starts in `rtreeFilter()`. Rowid lookup uses `%_rowid` to find the leaf node, builds one leaf search point, and locates the target cell. Normal scans acquire the root, deserialize numeric or callback constraints, enqueue the root at level `iDepth+1`, then call `rtreeStepToLeaf()`. `rtreeStepToLeaf()` repeatedly pops or expands search points, applies scalar constraints to internal or leaf cells, invokes registered geometry/query callbacks for `MATCH`, and enqueues matching children or leaf entries. The queue is score ordered for query callbacks and depth-first when scores tie.

Column retrieval in `rtreeColumn()` returns rowid, coordinate values, or lazily reads auxiliary columns from `%_rowid`. `rtreeNext()` resets any pending auxiliary read, pops the current point, and resumes the search. `rtreeRowid()` reads the current leaf cell's rowid from the active node.

Mutation in `rtreeUpdate()` handles SQLite virtual-table update conventions. It rejects writes while nodes are referenced by active readers, validates coordinate pairs, handles duplicate rowid conflicts with normal constraint or REPLACE semantics, deletes the old row when needed, chooses or allocates a new rowid, selects an insertion leaf with `ChooseLeaf()`, inserts using `rtreeInsertCell()`, and writes auxiliary values. Inserts may split nodes; deletes may condense the tree and reinsert orphaned node contents.

## State And Persistence Behavior
Persistent R-Tree state is entirely shadow-table backed. `%_node` contains fixed-size node blobs. `%_parent` is required for upward traversal during delete/update repair. `%_rowid` maps user rowids to leaf nodes and stores auxiliary columns. The root row in `%_node` always exists, even for empty trees.

In-memory nodes are reference-counted `RtreeNode` objects stored in a small hash by node id. Dirty nodes are written on final release. The module reuses one `sqlite3_blob` handle for reading node blobs and closes it on transaction boundaries, savepoints, disconnect, cursor drain, and operations that need to avoid locking shadow tables.

Insertion updates both structural blobs and mapping tables. For leaf cells, `rowidWrite()` updates `%_rowid`; for internal cells, `parentWrite()` updates `%_parent`. Split handling writes new node numbers, updates child parent mappings, and rewrites parent bounding boxes. Delete handling removes `%_rowid` entries, removes underfull nodes from `%_node` and `%_parent`, queues removed node contents in `pDeleted`, and reinserts those contents after condensation.

Coordinate persistence is big-endian 32-bit integer or 32-bit float. Floating-point writes deliberately round lower bounds down and upper bounds up via `rtreeValueDown()` and `rtreeValueUp()` so stored rectangles conservatively contain the requested values.

## Dependencies
The file depends on SQLite public/core APIs, `sqlite3ext.h` for loadable extension builds, `sqlite3rtree.h` for public callback types, and `sqlite3.h` in core builds. It uses virtual-table, blob, prepared-statement, typed pointer, value duplication, SQL string builder, and extension initialization APIs.

Compile-time branches cover `SQLITE_CORE`, `SQLITE_ENABLE_RTREE`, `SQLITE_OMIT_VIRTUALTABLE`, `SQLITE_RTREE_INT_ONLY`, `SQLITE_ENABLE_GEOPOLY`, debug/corruption checks, byte-order optimizations, and coverage/mutation test behavior. If geopoly is enabled, `geopoly.c` is included from this compilation unit.

## Integration Points
SQLite reaches this code through the virtual-table module API. SQL users see `CREATE VIRTUAL TABLE ... USING rtree(...)`, `rtree_i32(...)`, coordinate constraints, rowid lookup, `MATCH` queries backed by callback APIs, auxiliary columns, `rtreecheck()`, `rtreenode()`, and `rtreedepth()`.

The public header `sqlite3rtree.h` defines the callback structs consumed by this file. The Tcl test file in this subset registers callbacks against these APIs. SQLite integrity check integrates through module version 4 `xIntegrity`, returning `In RTree db.table:` diagnostics when shadow tables are inconsistent.

## Risks And Edge Cases
The largest risk is hostile or corrupt shadow-table content. The code checks invalid node sizes, impossible cell counts, bad root depth, parent loops, duplicate queued nodes, missing mapping rows, and malformed blobs, but many routines still operate close to raw byte buffers and depend on correct `nBytesPerCell` and fixed node sizes.

Node reference ownership is subtle. Parent pointers are themselves reference-counted; split, delete, and cached cursor paths must release and reacquire nodes in the right order. The code explicitly refuses writes while `nNodeRef` is non-zero because rebalancing under an active reader can invalidate cursor state.

R*-Tree splitting and reinsertion are correctness-sensitive. `splitNodeStartree()` chooses dimensions and split points by margin, overlap, and area. Mapping updates must follow every movement of child cells, or `%_parent`/`%_rowid` diverge from `%_node`.

Floating-point behavior is intentionally conservative and platform-sensitive. Byte order, float rounding, very large integer comparisons in `rtreeFilter()`, and `SQLITE_RTREE_INT_ONLY` all affect exact comparison semantics. Callback queries also depend on user callbacks returning valid `eWithin` and score values.

## Test Signals
Strong tests include creating, connecting, dropping, and renaming `rtree` and `rtree_i32` tables; verifying shadow table contents; rowid lookup; coordinate range scans; `NULL` and text constraint behavior; auxiliary columns; duplicate rowid conflict modes; REPLACE updates; delete-induced condensation; root height growth and shrink; savepoint/drop interactions; and read/write locking with active cursors.

Callback tests should cover legacy geometry callbacks, query callbacks with scores and `eWithin`, destructor paths, `pUser` cleanup, SQL parameter preservation through `apSqlParam`, and callback errors. Corruption tests should feed malformed node blobs, bad parent mappings, missing rowid mappings, bad depths, and inconsistent bounds into `rtreecheck()` and module scans.
