# sources/sync-backup/syncthing/lib/config/migrations_test.go

## sources/sync-backup/syncthing/lib/config/migrations_test.go

Purpose: Focused tests for selected migration behavior.

Important APIs/types/functions: `TestMigrateCrashReporting` applies the global migration set to version 28 configs. `TestMigrateReconnectInterval` applies version 52 migration behavior from version 51 inputs.

Control flow and state: Both tests lock `migrationsMut`, apply migrations in-place, and compare final option fields. Crash reporting becomes enabled if global discovery is enabled or usage reporting is accepted; reconnect interval is reduced to the minimum of the existing interval and the old QUIC interval formula.

Dependencies and integration: Exercises `migrations.apply` and option fields without loading XML fixtures.

Risks and test signals: These tests protect user-visible notification/reporting behavior and connection retry cadence changes across upgrades.
