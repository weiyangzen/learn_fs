# sources/storage-engines/sqlite/tool/max-limits.c

## Purpose
`max-limits.c` is a diagnostic utility that links against an SQLite library and prints the compile-time maximum values for SQLite runtime limits. It discovers each maximum by temporarily attempting to raise that limit to the largest signed 32-bit value and reading back SQLite's clamped value.

## Important APIs, Types, and Functions
- `aLimit[]` maps `SQLITE_LIMIT_*` categories to their corresponding `SQLITE_MAX_*` compile-time names.
- `maxLimit(sqlite3 *db, int eCode)` saves the current limit, calls `sqlite3_limit(db, eCode, 0x7fffffff)`, then restores the original value and returns the maximum.
- `main()` opens an in-memory database, iterates `aLimit`, prints aligned name/value pairs, and closes the DB.

## Control Flow
`main()` calls `sqlite3_open(":memory:", &db)`. If successful, it loops over `aLimit`, calls `maxLimit()` for each category, prints the result, then closes the database. If open fails, it exits silently without printing an error.

## State and Persistence Behavior
No persistent database state is created because the database is in-memory. Each limit is restored immediately after probing, so the database handle is left with original runtime limits until close.

## Dependencies and Integration Points
- Depends on `sqlite3.h`, `stdio.h`, and a linkable SQLite library.
- Reports limits affected by compile-time macros such as `SQLITE_MAX_LENGTH`, `SQLITE_MAX_COLUMN`, `SQLITE_MAX_VARIABLE_NUMBER`, and others.
- Useful in packaging, support, and test contexts where the effective library's compile options need verification.

## Risks and Edge Cases
- Failed `sqlite3_open()` is ignored, so diagnostics are absent on failure.
- The list only covers the hardcoded `SQLITE_LIMIT_*` categories present in this source; new SQLite limit categories require source changes.
- The method relies on `sqlite3_limit()` returning the old/current effective maximum when asked for a huge value, which is the intended SQLite API behavior.

## Test Signals
- Compile against a default SQLite build and compare printed values to documented defaults for that version.
- Compile against custom `SQLITE_MAX_*` settings and verify the tool reflects the custom maxima.
- Include a link/runtime library mismatch test to verify it reports the loaded library's limits, not just headers.
