<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask.go -->
# sources/sync-backup/kopia/internal/uitask/uitask.go

- Purpose: Defines UI task status/data and running-task behavior including cancellation, progress, counters, and in-memory JSON logs.
- Important APIs/types/functions: `Status`, `IsFinished`, `LogLevel`, `Info`, `runningTaskInfo`, `CurrentTaskID`, `OnCancel`, `cancel`, `ReportProgressInfo`, `ReportCounters`, `info`, `loggerForModule`, `uiLevelEncoder`, `addLogEntry`, `log`, `Write`, `Sync`.
- Control flow: Running tasks mutate their own state under a mutex, register cancel callbacks, transition to canceling, clone counters for reads, and collect zap JSON log entries while filtering noisy format logs and enforcing log count limits.
- State and persistence: In-memory task fields, counters, cancel callbacks, and bounded log slices; optional persistent file logging is coordinated in the manager.
- Dependencies and integration points: Integrates `zap`, `content.FormatLogModule`, and `repo/logging`.
- Risks and edge cases: Log filtering is byte-pattern-based, finished tasks ignore new log entries, and cancel callbacks run asynchronously.
- Test signals: `uitask_test.go` covers logs, counters, status, cancellation timing, retention, and summaries.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/uitask/uitask.go -->
