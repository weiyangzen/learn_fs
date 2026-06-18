<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_maintenance_test.go -->
# sources/sync-backup/kopia/internal/server/server_maintenance_test.go

- Purpose: Verifies maintenance manager behavior against a test repository and fake server implementation.
- Important APIs/types/functions: `testServer`, `runMaintenanceTask`, `refreshScheduler`, `enableErrorNotifications`, `notificationTemplateOptions`, `TestServerMaintenance`, `TestServerMaintenanceReadOnlyRepoConnection`.
- Control flow: Tests configure maintenance params in a direct write session, start the manager, trigger runs, wait for atomics to observe execution, inject one error, and verify retry backoff. The read-only case rewrites client options and reopens the repo before startup.
- State and persistence: Uses repository maintenance manifests/params plus in-memory atomics and a mutex-protected injected error in `testServer`.
- Dependencies and integration points: Uses `repotesting`, `repo.DirectWriteSession`, `maintenance.SetParams`, `clock`, and `testify/require`.
- Risks and edge cases: Timing assertions use `Eventually` and wall-clock intervals; tests disable error notifications, so notification-send behavior is not exercised here.
- Test signals: This is the direct test signal for `server_maintenance.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_maintenance_test.go -->
