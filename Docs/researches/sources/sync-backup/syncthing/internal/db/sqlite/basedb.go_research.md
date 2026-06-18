# sources/sync-backup/syncthing/internal/db/sqlite/basedb.go

## Purpose
This file contains shared SQLite database opening, schema migration, statement caching, template expansion, and maintenance helpers used by main and folder databases.

## Important APIs, Control Flow, And State
`baseDB` holds path metadata, an `sqlx.DB`, update checkpoint counters, a prepared-statement cache, and SQL template input values. `openBase` builds a file URI with common SQLite options, opens the DB, sets connection limits, applies pragmas, initializes `baseDB`, then uses one dedicated connection with foreign keys disabled and legacy alter table enabled to run schema and migrations inside a transaction. It filters migration scripts by schema version, reruns schema scripts after migrations, checks foreign keys when migrations ran, records `currentSchemaVersion`, commits, and optionally vacuums/optimizes. `stmt` caches prepared statements after template expansion. `runScripts` reads embedded SQL files by glob and splits statements on `\n;`. Schema version helpers persist and read migration metadata.

## State And Persistence
Persistent state includes SQLite schema, migration history, indexes/triggers from embedded SQL, and WAL/checkpoint side effects. Runtime state includes cached prepared statements protected by an RW mutex.

## Dependencies And Integration Points
It depends on `sqlx`, embedded SQL files, `build.LongVersion`, protocol flag constants used in SQL templates, logging, and SQLite driver constants from other package files. It underpins main DB and per-folder DB opening.

## Risks And Test Signals
`runScripts` depends on a repository convention that statement separators are lines beginning with semicolon; SQL files must preserve this. `stmt` caches by unexpanded template string, so template input must be stable after open. `Close` locks update and statement mutexes before closing statements and DB. Tests should cover path URI conversion on Windows/UNC paths, migration ordering, ignored script failures, foreign-key checks, statement cache concurrency, template expansion, and vacuum/checkpoint behavior after migration.
