# sources/storage-engines/sqlite/src/analyze.c

## Purpose

`analyze.c` implements the SQL `ANALYZE` command and the runtime loading of persisted planner statistics. It creates and refreshes `sqlite_stat1` and, when `SQLITE_ENABLE_STAT4` and the `SQLITE_Stat4` optimization are active, `sqlite_stat4`. The file is the bridge between table/index scans, VDBE bytecode, the internal query planner estimates stored on `Table` and `Index`, and persisted statistics rows in ordinary database tables.

## Important APIs, Types, And Functions

The main parser entry point is `sqlite3Analyze(Parse*, Token*, Token*)`, which accepts whole-database, single-database, table, and index forms. It delegates to `analyzeDatabase()` and `analyzeTable()`, which open statistic tables with `openStatTable()`, emit VDBE code with `analyzeOneTable()`, and then add `OP_LoadAnalysis` through `loadAnalysis()`.

STAT collection uses internal SQL functions, not public SQL APIs. `stat_init()` allocates a `StatAccum` blob, `stat_push()` observes sorted index rows and updates cardinality counters and optional samples, and `stat_get()` emits `sqlite_stat1` text or STAT4 sample fields. `StatSample` stores `nEq`, `nLt`, `nDLt`, sampled rowid/key material, sample priority, and tie-break hashes. `StatAccum` stores row counts, scan limits, current counters, periodic sampling cadence, sample arrays, and best-sample candidates.

The load side is centered on `sqlite3AnalysisLoad(sqlite3*, int)`. It clears prior planner stats, reads `sqlite_stat1` through `sqlite3_exec()` and `analysisLoader()`, decodes integer arrays with `decodeIntArray()`, applies flags such as `unordered`, `noskipscan`, `sz=`, and optional `costmult=`, then loads STAT4 samples through `loadStat4()` and `loadStatTbl()`. `sqlite3DeleteIndexSamples()` owns cleanup of `Index.aSample`, and `initAvgEq()` derives average equality estimates from loaded samples.

## Control Flow

For an `ANALYZE` statement, schema mutexes must already be held and `sqlite3ReadSchema()` must succeed. Whole-database analysis skips TEMP, starts a write operation per target database, creates or clears `sqlite_stat1` and optionally `sqlite_stat4`, then iterates the schema table hash. Per-table or per-index analysis deletes only matching stat rows by `tbl` or `idx`.

`analyzeOneTable()` ignores views, virtual tables, and SQLite system tables. It opens the table and each selected index, builds bytecode that scans the index in key order, compares current key prefixes with saved previous prefix registers, calls `stat_push()` with the left-most changed column, then inserts one `sqlite_stat1` row. If STAT4 is enabled and the analysis limit is zero, it also loops over samples returned by `stat_get()`, seeks the table row, builds the sampled record, and inserts `sqlite_stat4` rows.

The runtime loader reverses the process: `sqlite3AnalysisLoad()` resets `TF_HasStat1`, `Index.hasStat1`, and STAT4 sample arrays, reads stat rows into schema objects, defaults indexes with missing stats, optionally loads STAT4 rows into contiguous `IndexSample` allocations, and frees temporary `aiRowEst` arrays after STAT4 initialization.

## State And Persistence Behavior

Persistent state is stored in `sqlite_stat1` and `sqlite_stat4` inside each analyzed database. `openStatTable()` either creates these tables, clears all rows, or deletes rows for one table/index. In-memory planner state is stored on `Table.nRowLogEst`, `Table.tabFlags`, `Index.aiRowLogEst`, `Index.hasStat1`, `Index.bUnordered`, `Index.noSkipScan`, `Index.szIdxRow`, optional `Index.aSample`, `Index.aAvgEq`, and `Index.nRowEst0`.

`db->nAnalysisLimit` changes behavior substantially. With a limit, `stat_push()` can request skip-ahead behavior and STAT4 collection is disabled by setting `StatAccum.mxSample` to zero. Without a limit, the full scan can collect histogram samples. Memory ownership is delicate: `StatAccum` is returned as a blob with `statAccumDestructor`, STAT4 sample rowids may allocate per sample, and loaded sample blobs allocate eight zero guard bytes to protect corrupted-record comparisons from small overreads.

## Dependencies And Integration Points

This file depends on parser and schema services (`sqlite3ReadSchema`, `sqlite3FindTable`, `sqlite3FindIndex`, `sqlite3LocateTable`), VDBE construction (`OP_OpenRead`, `OP_OpenWrite`, `OP_Count`, `OP_Insert`, `OP_LoadAnalysis`), btree/schema mutex assertions, table/index metadata, collations, rowid and WITHOUT ROWID primary-key handling, authorization checks for `SQLITE_ANALYZE`, and optional preupdate-hook support. Planner consumers rely on loaded `Table` and `Index` estimates during query planning.

Compile-time and runtime gates include `SQLITE_OMIT_ANALYZE`, `SQLITE_ENABLE_STAT4`, `SQLITE_ENABLE_PREUPDATE_HOOK`, `SQLITE_ENABLE_COSTMULT`, `SQLITE_ENABLE_EXPLAIN_COMMENTS`, `SQLITE_DEBUG`, and the `SQLITE_Stat4` optimization flag.

## Risks And Edge Cases

The highest-risk areas are register lifetime in generated VDBE, prefix-change detection for unique, partial, expression, rowid, and WITHOUT ROWID indexes, and consistency between persisted stat text and planner fields. STAT4 sample ranking is subtle: it mixes periodic samples, high-cardinality duplicate prefixes, tie-break hashes, and delayed filling of zero `anEq` slots. Corrupt or manually edited `sqlite_stat` tables must not crash the loader. Duplicate stat rows are tolerated by clobbering or skipping, but they can change estimates. Analysis limits intentionally trade accuracy for speed and disable histogram generation.

## Test Signals

Useful signals include sqllogictest or TCL tests for `ANALYZE` forms, partial indexes, WITHOUT ROWID tables, expression indexes, `analysis_limit`, generated `sqlite_stat1` text, STAT4 sample counts, query-plan changes after `OP_LoadAnalysis`, malformed stat tables, OOM paths, and compile variants with and without STAT4. Assertions around schema mutexes, temp-register ranges, and `sqlite3NoTempsInRange()` are important debug-only signals for bytecode safety.
