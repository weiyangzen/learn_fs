<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/log.go -->
# sources/sync-backup/kopia/tests/robustness/engine/log.go

This file defines the robustness engine action log. `Log` holds all `LogEntry` records plus `ThisRunStartIdx`, and `LogEntry` captures `Time`, `Action`, command options, outputs, success state, and an error string. The formatting path is `LogEntry.String`, `formatTime`, `Log.StringThisRun`, and `Log.String`, which provide human-readable chronological diagnostics for all actions or only the current engine run.

The important API is append/find behavior: `AddEntry` appends a started action, `AddCompleted` mutates a started entry with completion state, and `FindLast`/`FindLastThisRun`/`findLastUntilIdx` find the most recent entry for an `ActionKey`. `setLogEntryCmdOpts` records action options deterministically enough for logs, while `Engine.logCompleted` ties engine action execution to stats persistence.

State is entirely in-memory until `metadata.go` serializes `EngineLog` into the configured metadata persister. Risks center on log entries being mutable after append, stringification losing structured error details, and callers needing to pass the same `LogEntry` pointer to completion. Test signals are indirect through engine robustness flows that depend on last snapshot/action lookup and persisted logs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/engine/log.go -->
