# sources/storage-engines/sqlite/test/fuzzinvariants.c

## Purpose

`fuzzinvariants.c` is a `fuzzcheck` support library that validates SQLite query-result invariants. Given a prepared statement positioned on `SQLITE_ROW`, it builds alternate SQL that should include the current row, executes it, and treats a missing row as a bug unless corruption, ambiguous ordering, collation behavior, virtual tables, or scalar subqueries plausibly explain the mismatch.

## Important APIs, Types, and Functions

- `fuzz_invariant()` is the exported entry point. It chooses an invariant by `iCnt`, prepares alternate SQL, binds current-row values, searches for a matching alternate row, and returns `SQLITE_OK`, `SQLITE_DONE`, `SQLITE_CORRUPT`, or an SQLite error.
- `fuzz_invariant_sql()` wraps the original SQL in a subquery and varies `DISTINCT`, `ORDER BY`, all-column predicates, and single-column predicates.
- `sameValue()` compares row values across statements, with special handling for numeric type compatibility, text encodings, BLOB/TEXT byte comparison, and optional collation-aware equality.
- `bindDebugParameters()` binds `$int_`, `$text_`, and optional carray debug parameters.
- `reportInvariantFailed()`, `printRow()`, and `printHex()` emit reproduction details before aborting on a final invariant failure.

## Control Flow

`fuzz_invariant()` exits when corruption is already known, parameter count is too high, or no invariant exists for `iCnt`. Every third check prepares the alternate query with optimizer flags inverted using `sqlite3_test_control(SQLITE_TESTCTRL_OPTIMIZATIONS)`. It then binds debug parameters and appends current row column values after original parameters. If the alternate result scan cannot find a matching row, it runs `PRAGMA integrity_check`, retries the original SQL with reverse scan order toggled, retries with an explicit collation comparison query, and inspects `bytecode(?1)` for virtual-table opens or scalar subqueries before reporting failure.

## State and Persistence Behavior

The file persists nothing. It temporarily mutates SQLite connection/test-control state, uses caller-owned `*pbCorrupt` to suppress later checks after corruption, and allocates transient SQL/buffers through SQLite allocators. Final unexplained mismatches abort the process by design.

## Dependencies and Integration Points

It depends on SQLite public APIs plus test/internal surfaces such as optimizer test controls, `SQLITE_DBCONFIG_REVERSE_SCANORDER`, `sqlite3_expanded_sql()`, `sqlite3_value_encoding()`, `bytecode(?)`, and optional `sqlite3_carray_bind()`. It is invoked by SQLite `fuzzcheck`.

## Risks and Test Signals

Risks include name-based predicate ambiguity, collation false positives, special behavior around virtual tables/scalar subqueries, and intentional process aborts. Useful signals are `SQLITE_OK`, `SQLITE_DONE`, `SQLITE_CORRUPT` with `*pbCorrupt=1`, verbose expanded SQL, and detailed abort reports containing original SQL, alternate SQL, missing row, and alternate results.
