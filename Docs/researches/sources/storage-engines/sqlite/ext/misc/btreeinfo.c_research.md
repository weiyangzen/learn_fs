# sources/storage-engines/sqlite/ext/misc/btreeinfo.c

## Purpose
`btreeinfo.c` implements the read-only eponymous-only virtual table `sqlite_btreeinfo`, which reports schema b-trees and estimated structural metrics such as entries, page count, depth, page size, and rowid presence.

## Important APIs, types, and functions
- `BinfoTable` stores the SQLite connection.
- `BinfoCursor` stores the `sqlite_schema` scan statement, selected schema, last step result, and lazily computed b-tree metrics.
- `binfoConnect()` declares columns including hidden `zSchema`.
- `binfoBestIndex()` recognizes equality constraints on hidden schema.
- `binfoFilter()` queries `sqlite_schema` plus a synthetic `sqlite_schema` root row.
- `binfoCompute()` reads pages from `sqlite_dbpage('main')` and estimates tree depth, pages, entries, page size, and rowid status.
- `sqlite3BinfoRegister()` and `sqlite3_btreeinfo_init()` register the module.

## Control flow
A scan prepares a schema query for `main` or the constrained schema. Columns copied from `sqlite_schema` are returned directly. When a metric column is requested, `binfoColumn()` lazily calls `binfoCompute()` for the row's root page. `binfoCompute()` walks from root toward a representative leaf by reading b-tree pages through `sqlite_dbpage`, multiplying observed cell fanout to estimate total entries/pages and stopping at leaf page types.

## State and persistence behavior
No data is persisted. Cursor state holds prepared statements and cached metrics for the current row. The table reads database pages and schema metadata from the active connection.

## Dependencies and integration points
It depends on SQLite virtual table APIs and the `sqlite_dbpage` virtual table being available. It uses raw SQLite database page format assumptions, including page-1 header offset and b-tree page type bytes.

## Risks and edge cases
- The header labels this extension unused, untested, unsupported, and demonstration-only.
- Metrics are estimates based on one root-to-leaf path, not full traversal.
- `binfoCompute()` hardcodes `sqlite_dbpage('main')`, while the outer scan can constrain `zSchema`; attached-schema page reads may not match the requested schema.
- Corrupt pages, excessive depth, or malformed cell pointers return errors.
- `BINFO_COLUMN_SZPAGE` is defined but not handled in `binfoColumn()`, so `szPage` is not returned despite being declared.

## Test signals
Tests should load `sqlite_dbpage`, query `sqlite_btreeinfo`, compare schema columns against `sqlite_schema`, verify hidden-schema constraint planning, exercise WITHOUT ROWID and index rows, and validate graceful errors on corrupt or missing page data.
