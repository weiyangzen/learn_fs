# sources/storage-engines/sqlite/src/dbpage.c

## Purpose

`dbpage.c` implements the optional `sqlite_dbpage` virtual table, available for test builds or `SQLITE_ENABLE_DBPAGE_VTAB` when virtual tables are enabled. It exposes raw database pages through pager APIs so reads see uncommitted and WAL-backed changes, and writes can replace pages or request truncation.

## Important APIs, Types, and Functions

- `DbpageCursor` stores scan state: page number range, pager pointer, page-1 reference, schema index, and page size.
- `DbpageTable` stores the owning `sqlite3` connection plus pending truncate target (`iDbTrunc`, `pgnoTrunc`).
- `dbpageConnect()` declares `pgno INTEGER PRIMARY KEY`, `data BLOB`, and hidden `schema`; configures the module as `SQLITE_VTAB_DIRECTONLY` and all-schema aware.
- `dbpageBestIndex()` plans optional `schema=` and `pgno=` constraints.
- `dbpageFilter()` resolves the schema, pager, page size, last page, optional page number, and pins page 1.
- `dbpageColumn()` returns page number, raw page blob, or schema name; the pending-byte page is returned as a zero blob.
- `dbpageUpdate()` implements replacement/insert-like writes and insert-NULL truncation requests.
- `dbpageBeginTrans()`, `dbpageBegin()`, `dbpageSync()`, and `dbpageRollbackTo()` coordinate write transaction and delayed truncation.
- `sqlite3DbpageRegister()` registers `"sqlite_dbpage"`.

## Control Flow and Behavior

Queries default to the main schema unless a usable hidden `schema=` constraint supplies another database name. Full scans visit page 1 through `sqlite3BtreeLastPage()`, while `pgno=` constrains the scan to one page or no rows if out of range. The cursor keeps a page-1 reference while scanning, likely to stabilize pager state and database header access.

Data reads use `sqlite3PagerGet()` on each requested page and return a transient copy of exactly one page. The page containing `PENDING_BYTE` is treated specially because requesting it from the pager is corrupt; the module returns a zero blob of page size.

Writes are disallowed under defensive mode and delete operations are rejected. Updates require matching old/new page numbers; inserts behave as replacement. The target page must be in `1..4294967294`. Data must be a blob of exact page size, except `INSERT` with NULL data and `pgno > 1`, which records a pending truncation to `pgno-1`. Writes open transactions on all attached B-trees because the module cannot know in advance which schema might be updated. Actual page bytes are copied after `sqlite3PagerWrite()`. Truncation is delayed until xSync via `sqlite3PagerTruncateImage()`.

## State and Persistence

Read scans hold pager references. Successful blob writes mutate database pages within the surrounding SQLite transaction. Truncation state is table-level and pending until sync; rollback-to and new transactions clear it. Defensive mode prevents writes, and normal pager journaling/WAL semantics provide durability or rollback.

## Dependencies and Integration Points

This file depends on virtual table APIs, B-tree and pager internals, schema-name lookup, table-valued function support, transaction hooks, `SQLITE_Defensive`, and the pending-byte constant. It integrates with SQL as the `sqlite_dbpage` eponymous module and is intentionally direct-only to block unsafe use from schema objects such as triggers or views.

## Risks and Edge Cases

The module can corrupt databases if misused, which is why direct-only and defensive checks matter. Truncation uses `INSERT(pgno,NULL)` semantics and is staged; errors after staging must clear `pgnoTrunc`. Opening write transactions on all databases may have locking side effects. The pending-byte page behavior is synthetic. Page-size mismatches, invalid schema names, bad page numbers, attempts to delete, and attempts to change page numbers must report errors through `zErrMsg`.

## Test Signals

Tests should cover full scans and single-page scans, attached schema selection, unknown schema returning no rows or error depending path, reads through WAL/uncommitted pager state, pending-byte zero blob, exact page-size enforcement, defensive-mode read-only errors, update versus insert page-number rules, insert NULL truncation and rollback cancellation, transaction opening failures, and disabled-module registration stubs.
