<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/sqlite3expert.c -->
# sources/storage-engines/sqlite/ext/expert/sqlite3expert.c

## Purpose
`sqlite3expert.c` implements SQLite's index-advisor engine. Given a live database connection and SQL workload, it mirrors schema into in-memory databases, compiles workload statements against instrumented virtual tables to observe constraints and ordering, generates candidate indexes, optionally synthesizes `sqlite_stat1`, asks SQLite's planner which candidates it would use, and exposes reports through the public `sqlite3expert` API.

## Important APIs, Types, And Functions
The exported API is `sqlite3_expert_new()`, `sqlite3_expert_config()`, `sqlite3_expert_sql()`, `sqlite3_expert_analyze()`, `sqlite3_expert_count()`, `sqlite3_expert_report()`, and `sqlite3_expert_destroy()`.

`struct sqlite3expert` holds the user database `db`, two in-memory databases `dbm` and `dbv`, table metadata, observed scans, observed writes, loaded statements, candidate-index hash state, the sample percentage, and the final candidate report string. `dbv` hosts expert virtual tables that observe planner constraints during prepare. `dbm` hosts a copied schema plus proposed indexes and statistics for final query-plan evaluation.

Core internal data types are `IdxTable` and `IdxColumn` for schema metadata, `IdxScan` for one observed table scan, `IdxConstraint` for equality, range, and order terms, `IdxWrite` for DML operations that may fire triggers, `IdxStatement` for each workload statement, and `IdxHash`/`IdxHashEntry` for deduplicating candidate indexes and mapping generated index names to SQL text and optional stat strings.

The virtual table module uses `expertConnect()`, `expertBestIndex()`, `expertFilter()`, cursor methods, and `idxRegisterVtab()`. `expertBestIndex()` is the instrumentation point: it records usable equality/range constraints and ORDER BY columns into `IdxScan` whenever SQLite prepares workload SQL against `dbv`.

Candidate generation is centered on `idxCreateCandidates()`, `idxCreateFromWhere()`, `idxCreateFromCons()`, and `idxFindCompatible()`. The code builds equality-prefix indexes, variants with range terms, and variants extended with ORDER BY terms, while avoiding candidates compatible with existing indexes in `dbm`.

Statistics and reporting are handled by `idxPopulateStat1()`, `idxPopulateOneStat1()`, `idxFindIndexes()`, and `idxAppendText()`. `idxFindIndexes()` parses `EXPLAIN QUERY PLAN` detail strings to identify which generated candidate index names the planner selected for each statement.

## Control Flow
`sqlite3_expert_new()` allocates the handle, opens `dbv` and `dbm` as `:memory:` databases, enables trigger EQP on `dbm`, registers dummy collation callbacks, optionally mirrors user-defined scalar/aggregate/window functions, copies the user's schema into `dbm`, creates an instrumented virtual-table schema in `dbv`, and installs an authorizer on `dbv` to notice writes.

`sqlite3_expert_sql()` may be called repeatedly before analysis. For each complete SQL statement, it first prepares against the real database to validate syntax and dependencies, then prepares against `dbv`. Preparing against expert virtual tables invokes `xBestIndex`, which appends `IdxScan` objects describing equality constraints, range constraints, ORDER BY columns, collations, and non-primary-key columns. The statement text returned by `sqlite3_sql()` is copied into an `IdxStatement`. If any statement in the supplied buffer fails, newly added scans and statements from that call are rolled back to the saved list heads.

`sqlite3_expert_analyze()` first processes writes and triggers. The authorizer records direct INSERT/UPDATE/DELETE operations as `IdxWrite` entries. `idxProcessTriggers()` recreates affected tables and triggers in `dbv`, renames the table to a unique temporary name, prepares synthetic DML, and thereby discovers scans inside trigger bodies. It loops because trigger processing may discover more writes.

After scan collection, `idxCreateCandidates()` walks every `IdxScan`. Equality constraints are collected without duplicate columns; range and ORDER BY tails are appended when useful; `idxCreateFromCons()` renders a `CREATE INDEX` statement, generates a deterministic hash-derived name, checks for collisions against schema object names, creates the index in `dbm`, and records the candidate in `hIdx`.

If sampling is enabled, `idxPopulateStat1()` runs `ANALYZE`, enables writable schema, creates helper SQL functions, and computes stat1 rows for all indexes in `dbm`. With `iSample==100`, it scans real user tables. With partial sampling, `idxBuildSampleTable()` creates a temp table in `dbv` using `sqlite_expert_sample()` to keep an approximate percentage of rows, then statistics are derived from the sample. `idxPopulateOneStat1()` sorts values according to each index key, uses `sqlite_expert_rem()` to compare current and previous key values, computes cardinality estimates, writes rows to `sqlite_stat1`, and stores candidate stat strings back into `hIdx`.

Finally, candidate report text is assembled, `idxFindIndexes()` runs `EXPLAIN QUERY PLAN` for each workload statement against `dbm`, matches `USING INDEX` and `USING COVERING INDEX` names back to generated candidates, and records per-statement recommended index SQL plus plan detail. A successful analyze sets `bRun`, after which `sqlite3_expert_report()` can return report buffers.

## State And Persistence Behavior
The expert object owns all analysis state. It never creates recommended indexes in the caller's database. It does read real schema and, depending on sample mode, may read real table data. Schema copies, candidate indexes, sampled rows, helper functions, and generated `sqlite_stat1` data live in the in-memory `dbm` or `dbv` connections.

`sqlite3_expert_sql()` is transactional with respect to each input buffer's internal lists: on error, it frees scans/statements added by that call and restores prior list heads. After `sqlite3_expert_analyze()` runs, `bRun` prevents further SQL additions. On analysis error, the public header documents the handle as no longer useful except for destruction.

Memory ownership is manual and SQLite-allocator-based. Table, scan, constraint, write, statement, hash, candidate, and statistics buffers are released by `sqlite3_expert_destroy()` or by local cleanup helpers. Returned report strings are borrowed pointers owned by the expert handle and remain valid until destruction.

## Dependencies
This implementation depends deeply on SQLite internals exposed through the public extension API: virtual tables, `sqlite3_index_info`, `sqlite3_vtab_collation()`, authorizer callbacks, schema pragmas, introspection pragmas, `pragma_function_list()`, `PRAGMA table_xinfo`, `PRAGMA index_list`, `PRAGMA index_xinfo`, `EXPLAIN QUERY PLAN`, `ANALYZE`, writable `sqlite_stat1`, custom collations, and user-defined SQL functions.

Compilation is excluded when `SQLITE_OMIT_VIRTUALTABLE` is defined. User-defined function mirroring is compiled only when schema and introspection pragmas are available. The file also uses SQLite allocation, formatting, randomness, and keyword APIs.

## Integration Points
The public header and standalone CLI call this API directly. The test harness in `test_expert.c` wraps the same API for Tcl. Inside SQLite, the code integrates with the query planner by deliberately preparing SQL against virtual tables and letting normal `xBestIndex` calls expose planner-visible constraints. It integrates with trigger analysis through SQLite's authorizer and prepare-time trigger compilation.

The candidate indexes and plans are ordinary SQLite SQL text and EQP detail strings, so downstream tools can present them without linking to private data structures.

## Risks And Edge Cases
`idxNewConstraint()` allocates `sizeof(IdxConstraint) * nColl + 1` instead of `sizeof(IdxConstraint) + nColl + 1`, which overallocates for non-empty collation names and is wasteful but generally safe. Candidate index naming retries at most fifty schema-name collisions and maps failure to `SQLITE_BUSY_TIMEOUT` with a specific public error path. EQP parsing is string-based and depends on detail text containing `USING INDEX` or `USING COVERING INDEX`, so changes to planner output wording can hide selected candidates.

The unique temporary table name is assumed not to collide with user objects; the file documents that conflicting user names can cause trigger analysis to ignore triggers on that table. Sampling uses randomness and approximate target ratios, so partial-stat recommendations may be nondeterministic. Dummy collations and dummy UDFs assert if executed; the design assumes they are needed only for prepare-time compatibility, not VDBE execution. Some file-local helper functions such as `dummyCompare`, `useDummyCS`, and UDF registration functions are not `static`, which widens symbol visibility in non-amalgamation builds.

## Test Signals
Strong tests should cover equality, range, ORDER BY, DESC, collation, covering-index, and existing-index compatibility cases; plans with no new indexes; partial and zero sampling; views; triggers fired by INSERT/UPDATE/DELETE; custom collations; user-defined scalar, aggregate, and window functions; virtual tables with missing modules; quoted identifiers and SQL keywords; and candidate-name collision handling. Existing direct test signal comes from the Tcl wrapper in `test_expert.c`, which allows SQLite's Tcl test suite to create expert handles, add SQL, analyze, count statements, and inspect each report channel.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/sqlite3expert.c -->
