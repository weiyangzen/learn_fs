# sources/storage-engines/sqlite/ext/misc/templatevtab.c

## Purpose
Provides a minimal eponymous-only read-only virtual table template for extension authors. The concrete sample table returns 10 rows with columns `a` and `b`.

## Important APIs, Types, And Functions
Types are `templatevtab_vtab` and `templatevtab_cursor`. Module methods include `templatevtabConnect`, `templatevtabDisconnect`, `templatevtabOpen`, `templatevtabClose`, `templatevtabFilter`, `templatevtabNext`, `templatevtabEof`, `templatevtabColumn`, `templatevtabRowid`, and `templatevtabBestIndex`. `sqlite3_templatevtab_init()` registers module `templatevtab`.

## Control Flow
`xConnect` declares `CREATE TABLE x(a,b)` and allocates the table object. `xOpen` allocates a cursor. `xFilter` initializes rowid to 1, `xNext` increments rowid, `xEof` stops at rowid >= 10, and `xColumn` returns `1000+rowid` for `a` and `2000+rowid` for `b`. `xBestIndex` reports fixed cost and row estimate.

## State And Persistence Behavior
There is no persistent state. The only cursor state is `iRowid`; the table object has no additional fields beyond the base object.

## Dependencies And Integration Points
Depends on SQLite extension and virtual table APIs. It intentionally implements only required methods and leaves write, transaction, rename, shadow-name, and integrity hooks null.

## Risks And Edge Cases
As a template, it is intentionally incomplete for real applications. It ignores constraints and arguments, is read-only, eponymous-only, and returns fixed estimates. Authors copying it must add validation, constraints, storage, and error handling appropriate to their domain.

## Test Signals
The basic test is loading the module and verifying `SELECT rowid,a,b FROM templatevtab` returns 9 visible rows with rowids 1 through 9 under the current `iRowid>=10` EOF rule, plus clean open/close under repeated scans.
