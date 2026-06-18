# sources/storage-engines/sqlite/ext/rtree/geopoly.c

## Purpose

`geopoly.c` implements SQLite's `geopoly` virtual table module and its polygon SQL functions. The module is an R-Tree-backed table specialized for two-dimensional polygons: it stores the original polygon in an auxiliary `_shape` column and indexes each shape by its bounding box. The file is included at the end of `rtree.c`, giving it direct access to internal R-Tree types, helpers, cursor logic, shadow-table handling, and integrity routines.

## Important APIs, Types, and Functions

`GeoCoord` is a `float`; `GeoPoly` is the in-memory and on-disk polygon representation with a 4-byte endian/count header followed by X/Y coordinate pairs. The on-disk polygon omits the repeated closing vertex required by GeoJSON. `GeoParse` tracks JSON parsing state. `GeoBBox` is aggregate state for `geopoly_group_bbox()`. `GeoEvent`, `GeoSegment`, and `GeoOverlap` implement a sweep-line overlap classifier.

Polygon parsing and conversion are handled by `geopolyParseJson()` and `geopolyFuncParam()`. They accept GeoJSON-like text arrays or geopoly blobs, normalize blob endianness, validate vertex counts and blob sizes, and allocate a `GeoPoly`. Scalar/aggregate SQL functions include `geopoly_blob`, `geopoly_json`, `geopoly_svg`, `geopoly_xform`, `geopoly_area`, `geopoly_ccw`, `geopoly_regular`, `geopoly_bbox`, `geopoly_group_bbox`, `geopoly_contains_point`, `geopoly_within`, `geopoly_overlap`, and optional `geopoly_debug`.

Virtual table entry points are `geopolyCreate()`, `geopolyConnect()`, `geopolyBestIndex()`, `geopolyFilter()`, `geopolyColumn()`, `geopolyUpdate()`, and `geopolyFindFunction()`, packaged in `geopolyModule`. Other module slots delegate to R-Tree implementations such as `rtreeOpen`, `rtreeNext`, `rtreeEof`, `rtreeRowid`, `rtreeDestroy`, transaction hooks, rename, shadow-name, and integrity checks. `sqlite3_geopoly_init()` registers functions, the aggregate, and the module.

## Control Flow

Scalar functions first decode their polygon arguments through `geopolyFuncParam()`. JSON parsing scans a strict array of coordinate arrays, requires at least four vertices including a closing vertex equal to the first, then removes the duplicate close point for storage. Blob parsing checks the endian flag and byte length, copies data into a mutable `GeoPoly`, and byte-swaps coordinates if the blob endian differs from the host.

Geometry helpers then operate on that normalized representation. `geopolyArea()` computes signed area and `geopolyCcwFunc()` reverses vertices except the first when winding is clockwise. `geopolyBBox()` computes min/max X/Y and either fills R-Tree coordinates or returns a four-vertex bounding-box polygon. `geopolyContainsPointFunc()` uses a ray-crossing style `pointBeneathLine()` test and reports outside, boundary, or inside. `geopolyOverlap()` builds non-vertical segments for both polygons, sorts add/remove events by X, maintains an active list sorted by Y and slope, detects crossings, and classifies disjoint, overlap, containment, or equality based on side masks.

For virtual tables, `geopolyInit()` declares a schema beginning with `_shape` plus user-specified auxiliary columns, configures the backing `Rtree` for two real32 dimensions, initializes shadow storage through R-Tree helpers, and marks `_shape` as not-null auxiliary data. `geopolyBestIndex()` prefers rowid equality, then overloaded `geopoly_overlap(_shape, ?)` or `geopoly_within(_shape, ?)` constraints, then full scan. `geopolyFindFunction()` maps those function names to special constraint opcodes so `xBestIndex` can see them.

`geopolyFilter()` turns an overlap or within function argument into four bounding-box constraints and then uses the normal R-Tree search machinery. The SQL function itself is not omitted, so exact polygon filtering still runs after the bounding-box prefilter. `geopolyColumn()` reads `_shape` and auxiliary columns from the R-Tree aux table using prepared read SQL. `geopolyUpdate()` handles deletes, inserts, rowid changes, shape updates, conflict handling, R-Tree cell insertion/deletion, and auxiliary table writes. Text shapes are converted to canonical geopoly blobs before storage.

## State and Persistence Behavior

Persistent state follows the R-Tree shadow-table model created by `rtreeSqlInit()`: nodes store rowid and four bounding coordinates, while auxiliary storage stores `_shape` and user columns. `_shape` is always counted as an auxiliary not-null column. Insert and update operations derive `cell.aCoord` from the polygon bounding box; if `_shape` is unchanged, coordinate updates can be skipped and only auxiliary values are updated. If `_shape` changes or the rowid changes, the old R-Tree row is deleted and a new cell is inserted.

Function calls allocate temporary `GeoPoly` objects and free them before return. Aggregation uses SQLite aggregate context to accumulate one bounding box. The virtual table maintains standard R-Tree cursor, node reference, and prepared-statement state through the surrounding `rtree.c` infrastructure.

## Dependencies and Integration Points

This file depends on SQLite core function APIs, `sqlite3_str`, deterministic/innocuous/direct-only function flags, virtual table APIs including overloaded function constraints, and many private R-Tree definitions from `rtree.c`: `Rtree`, `RtreeCursor`, `RtreeNode`, `RtreeCell`, `RtreeCoord`, `RtreeConstraint`, `rtreeModule`, `getNodeSize()`, `rtreeSqlInit()`, `rtreeReference()`, `rtreeRelease()`, `findLeafNode()`, `nodeAcquire()`, `nodeRelease()`, `rtreeSearchPointNew()`, `rtreeStepToLeaf()`, `nodeGetRowid()`, `rtreeDeleteRowid()`, `rtreeNewRowid()`, `ChooseLeaf()`, `rtreeInsertCell()`, and related transaction/integrity helpers.

The module integrates with SQL through `CREATE VIRTUAL TABLE ... USING geopoly(...)`, scalar geometry functions, aggregate bbox computation, and query planning for `geopoly_overlap()`/`geopoly_within()` predicates. Compile-time integration is controlled by SQLite R-Tree/geopoly capability flags, and debug output is conditional on `GEOPOLY_ENABLE_DEBUG`.

## Risks and Edge Cases

Geometry uses 32-bit floats for stored coordinates and exact equality comparisons in several places, including closing-vertex validation, boundary detection, and segment ordering. That keeps storage compact and matches R-Tree real32 coordinates, but precision-sensitive polygons can classify differently from double-precision GIS engines. The JSON parser is intentionally narrow: it accepts a simple coordinate-ring array and does not implement full GeoJSON objects, holes, multipolygons, or property containers.

The overlap algorithm ignores vertical segments in the sweep-line event set and handles containment/equality through side-mask intervals. Boundary-heavy or degenerate polygons are therefore important regression targets. `geopoly_contains_point()` documentation comments and implementation differ in wording: the code returns `1` for boundary and `2` for inside.

Because this file reaches into R-Tree internals, changes to `rtree.c` private struct layout, aux-column SQL generation, node locking, shadow-name policy, or constraint op encoding can break geopoly without changing this file. `geopolyUpdate()` must preserve R-Tree constraints while also storing canonical blob data; conflict handling depends on `sqlite3_vtab_on_conflict()` and the existing `pReadRowid` statement.

`geopoly_svg()` appends caller-supplied attribute text directly into the generated SVG fragment. It is an SQL rendering helper, not an HTML sanitizer.

## Test Signals

Direct signals include geopoly-capable R-Tree tests, especially `ext/rtree/rtreefuzz001.test`, which creates geopoly data and queries `geopoly_overlap()` with rendered SVG output. Broader R-Tree tests exercise shared cursor, update, integrity, shadow table, and query-planning behavior used by geopoly because the module delegates most virtual table mechanics to `rtree.c`. Useful checks are canonical blob/json round trips, bbox values, point containment return codes, overlap and within classifications, rowid lookup plans, function-constraint plans, insert/update/delete behavior, conflict replacement, and `rtreecheck`/integrity validation of geopoly shadow storage.
