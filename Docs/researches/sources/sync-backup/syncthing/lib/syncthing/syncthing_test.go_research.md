# sources/sync-backup/syncthing/lib/syncthing/syncthing_test.go

Purpose: tests selected app startup validation and failure cleanup.

Important tests: `TestShortIDCheck` builds configs with non-conflicting and conflicting first-64-bit device IDs and asserts `checkShortIDs` behavior. `TestStartupFail` creates an in-memory certificate, constructs a conflicting device ID with the same short ID, starts an app with temp SQLite DB, expects `Start` to fail, verifies `Wait` returns within one second with `ExitError`, checks `Error` matches the startup error, and confirms the DB was closed.

State and persistence: uses temp config files and temp SQLite DBs.

Dependencies and integration: exercises config wrapping, TLS certificate generation, protocol device IDs, app lifecycle, and DB close behavior.

Risks and signals: good coverage for a critical startup failure path. It does not cover successful startup, GUI setup, migrations, or service runtime errors.
