# sources/sync-backup/syncthing/lib/stats/stats_test.go

Purpose: provides basic coverage for device statistics persistence.

Important tests: `TestDeviceStat` opens a temporary SQLite DB, wraps a typed namespace, writes `WasSeen` and a 42-second connection duration, reads `GetStatistics`, and asserts `LastSeen` is recent and duration seconds equals 42.

State and persistence: uses a real temporary SQLite database and closes it in cleanup.

Dependencies and integration: exercises `internal/db/sqlite` and `db.Typed`, so it catches serialization/storage regressions in addition to stats code.

Risks and signals: useful smoke test for device stats. It does not cover default values, database error paths, folder stats, or partial write scenarios.
