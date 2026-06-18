# sources/sync-backup/kopia/repo/maintenance/maintenance_schedule_test.go

Purpose: tests encrypted maintenance schedule persistence and next-maintenance timing logic.

Important APIs/types/functions: `TestMaintenanceSchedule`, `TestTimeToAttemptNextMaintenance`, and `toJSON`.

Control flow: format-specific schedule tests save and reload schedules and run info. Timing tests exercise enabled/disabled cycles, zero next times, ownership checks, and quick-vs-full ordering.

State/persistence behavior: creates repository schedule blobs through `SetSchedule`/`GetSchedule`; timing cases use parameter and schedule state.

Dependencies/integration: uses repository test environments, maintenance params, and JSON comparison helpers.

Risks/test signals: catches encryption/decryption, JSON shape, run history, and ownership regressions. Does not inspect raw ciphertext beyond behavior.
