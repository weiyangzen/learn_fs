# sources/sync-backup/syncthing/lib/syncthing/globalmigrations.go

Purpose: tracks global database migration version for app startup.

Important APIs and control flow: constants define `globalMigrationVersion = 1` and DB key `globalMigrationVersion`. `globalMigration` reads the previous version from misc DB, returns if already current, has no active migration steps, and writes version 1.

State and persistence: persists one misc DB int64 key. It is called during app startup after version bookkeeping and before model construction.

Dependencies and integration: depends on `internal/db` and `lib/config`. The config parameter is currently unused but leaves room for migration logic that needs configuration context.

Risks and signals: future migrations must preserve idempotence and error propagation. No dedicated tests in this subset.
