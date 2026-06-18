<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_maintenance.go -->
# sources/sync-backup/kopia/internal/server/server_maintenance.go

- Purpose: Implements the server-side background maintenance manager for direct, writable Kopia repositories.
- Important APIs/types/functions: `srvMaintenance`, `maintenanceManagerServerInterface`, `trigger`, `stop`, `beforeRun`, `afterFailedRun`, `refresh`, `refreshLocked`, `nextMaintenanceTime`, `maybeStartMaintenanceManager`.
- Control flow: startup rejects non-direct and read-only repositories, refreshes next maintenance time, then runs one goroutine selecting between a buffered trigger channel and a closed channel. A trigger clears cached schedule state, coalesces duplicate requests, runs `srv.runMaintenanceTask`, applies failure backoff, sends optional generic-error notifications, then refreshes scheduling.
- State and persistence: `cachedNextMaintenanceTime` and `nextMaintenanceNoEarlierThan` are mutex-protected in-memory scheduling state; durable maintenance configuration is read through `maintenance.TimeToAttemptNextMaintenance` from the direct repository.
- Dependencies and integration points: Uses `clock`, `repo.DirectRepository`, `repo/maintenance`, `notification`, `notifydata`, and `notifytemplate`; it plugs into the server scheduler through `refreshScheduler`.
- Risks and edge cases: Failure throttling is process-local, trigger coalescing can hide repeated requests by design, and notification delivery is best-effort through repository state.
- Test signals: Directly covered by `server_maintenance_test.go`, including successful run, scheduler refresh, failed-run backoff, and read-only repository rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_maintenance.go -->
