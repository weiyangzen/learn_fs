<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_manager.go -->
# sources/sync-backup/kopia/internal/uitask/uitask_manager.go

- Purpose: Manages lifecycle, lookup, cancellation, logs, summaries, and retention for UI-visible long-running tasks.
- Important APIs/types/functions: `Manager`, `Controller`, `TaskFunc`, `Run`, `ListTasks`, `WaitForTask`, `TaskSummary`, `TaskLog`, `GetTask`, `CancelTask`, `startTask`, `completeTask`, `NewManager`.
- Control flow: `Run` wraps context logging, starts a task, invokes the caller function synchronously, and completes the task. Lookup/list functions combine running and finished maps. Cancellation marks running tasks canceling and triggers callbacks. Completion records end time, final status, error message, and prunes oldest finished tasks.
- State and persistence: `Manager.mu` protects next ID, running map, and finished map. Logs are in memory unless `alsoLogToFile` adds the task logger to an existing persistent logger.
- Dependencies and integration points: Uses `clock`, `repo/logging`, and the `Controller` interface consumed by server snapshot/restore/maintenance tasks.
- Risks and edge cases: Lock ordering between manager and task mutexes must remain consistent; `WaitForTask` with negative wait uses an infinite loop interrupted only by context.
- Test signals: `uitask_test.go` directly exercises manager behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask_manager.go -->
