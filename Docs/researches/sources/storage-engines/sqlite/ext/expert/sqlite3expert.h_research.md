<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/sqlite3expert.h -->
# sources/storage-engines/sqlite/ext/expert/sqlite3expert.h

## Purpose
`sqlite3expert.h` is the public C API for SQLite's expert extension. It declares the opaque expert handle, configuration entrypoint, SQL-loading and analysis functions, report accessors, report/config constants, and destructor used by both the standalone CLI and test bindings.

## Important APIs, Types, And Functions
`typedef struct sqlite3expert sqlite3expert;` keeps implementation details private.

`sqlite3_expert_new(sqlite3 *db, char **pzErr)` constructs an analysis object over an existing SQLite connection and returns an SQLite-allocated error string on failure.

`sqlite3_expert_config(sqlite3expert *p, int op, ...)` currently supports `EXPERT_CONFIG_SAMPLE`, an integer percentage controlling whether analysis uses no stat1 data, full table scans, or sampled table rows.

`sqlite3_expert_sql(sqlite3expert *p, const char *zSql, char **pzErr)` parses complete SQL statements from a buffer and adds them to the workload. It must be called before analysis and is all-or-nothing for each buffer.

`sqlite3_expert_analyze(sqlite3expert *p, char **pzErr)` performs candidate generation, statistics synthesis, and planner evaluation. After it runs, no more SQL can be added.

`sqlite3_expert_count()` returns the number of loaded statements. `sqlite3_expert_report()` returns one of `EXPERT_REPORT_SQL`, `EXPERT_REPORT_INDEXES`, `EXPERT_REPORT_PLAN`, or `EXPERT_REPORT_CANDIDATES`. `sqlite3_expert_destroy()` frees the handle.

## Control Flow
The intended lifecycle is explicit: create with `sqlite3_expert_new()`, optionally configure sampling, add SQL with one or more `sqlite3_expert_sql()` calls, run `sqlite3_expert_analyze()`, inspect counts and reports, then destroy the handle. Report calls are meaningful only after successful analysis. Statement-indexed report modes use zero-based statement numbers and return NULL for out-of-range indexes.

## State And Persistence Behavior
The header documents borrowed report-string ownership and SQLite-allocated error-string ownership. Callers free errors with `sqlite3_free()`, but must not free report pointers. The expert object owns all internal analysis state until `sqlite3_expert_destroy()`.

Sampling controls performance and recommendation fidelity. Values less than or equal to zero disable stat1 generation, values greater than or equal to one hundred use complete stat1 data, and intermediate values sample that percentage of rows. The API does not promise deterministic output for sampled analysis.

## Dependencies
The only required include is `sqlite3.h`. The API uses SQLite result codes, `sqlite3*`, SQLite memory allocation conventions, and variadic C calls for configuration.

## Integration Points
`expert.c` uses this API to implement the command-line tool. `test_expert.c` exposes it to Tcl tests. Embedders can call it directly when they want index recommendations for a workload without creating proposed indexes in the production database.

## Risks And Edge Cases
The variadic config function requires callers to pass the exact expected argument type for each op; misuse is not type-checked by the compiler. After `sqlite3_expert_analyze()` fails, the object is documented as no longer useful except for destruction. `sqlite3_expert_count()` may count statements rather than calls, so callers should not assume one SQL buffer maps to one report slot.

The comment for `sqlite3_expert_destroy()` says `sqlite3-expert_new()` instead of `sqlite3_expert_new()`, a documentation typo only. The report constants are stable integer values used by tests and wrappers.

## Test Signals
Header-level contract tests should verify lifecycle misuse (`sqlite3_expert_sql()` after analysis returns `SQLITE_MISUSE`), sample clamping through config, out-of-range report indexes returning NULL, NULL index reports for statements needing no new indexes, and error-message ownership on invalid SQL.
<!-- END_FILE_RESEARCH: sources/storage-engines/sqlite/ext/expert/sqlite3expert.h -->
