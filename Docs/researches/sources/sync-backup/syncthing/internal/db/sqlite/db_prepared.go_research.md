# sources/sync-backup/syncthing/internal/db/sqlite/db_prepared.go

## Purpose
This file provides transaction-scoped prepared-statement caching for SQLite update paths.

## Important APIs and Control Flow
`txPreparedStmts` embeds `*sqlx.Tx` and keeps a `map[string]*sqlx.Stmt`. `Preparex` lazily creates the map, returns a cached statement for repeated identical SQL text, or prepares and stores a new statement with wrapped errors. `Commit` and `Rollback` close all cached statements before delegating to the underlying transaction.

## State and Persistence Behavior
The only state is in-memory and scoped to one transaction. It reduces repeated statement preparation in update and recalculation loops, especially `folderDB.Update`, `recalcGlobalForFile`, block insertion, and folder-wide recalculation.

## Dependencies and Integration Points
The file depends on `sqlx.Tx`, `sqlx.Stmt`, and `wrap`. `folderdb_update.go` is the primary caller.

## Risks and Test Signals
Because statement cache keys are raw query strings, whitespace or dynamic SQL changes create separate prepared statements. Closing errors are ignored. Correctness depends on always using `Commit` or `Rollback` on the wrapper, not directly on `Tx`, after statements have been cached.
