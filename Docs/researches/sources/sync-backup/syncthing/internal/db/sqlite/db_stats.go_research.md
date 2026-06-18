# sources/sync-backup/syncthing/internal/db/sqlite/db_stats.go

## Purpose
This file exposes SQLite table-size statistics for the main database and child folder databases.

## Important APIs and Types
`DatabaseStatistics` is a JSON-oriented tree with database name, optional folder ID, table stats, total stats, and child databases. `TableStatistics` holds table/index name, total size, and unused bytes. `DB.Statistics` reads stats for the main `baseDB`, then calls `forEachFolder` and appends one child entry per folder. `baseDB.tableStats` queries the SQLite `dbstat` virtual table with `aggregate=true`, orders by name, and sums table sizes.

## State and Persistence Behavior
The code is read-only, but requires SQLite to have the `dbstat` virtual table available. Results reflect current database pages and unused page bytes after any maintenance/vacuum state.

## Dependencies and Integration Points
It depends on `baseDB.stmt`, `folderDB.tableStats`, and `forEachFolder`. The statistics shape is likely consumed by diagnostics or API layers.

## Risks and Test Signals
Missing `dbstat` support or driver differences can make `Statistics` fail. There are no direct tests in this subset, so changes should be validated against both drivers and with at least one opened folder DB.
