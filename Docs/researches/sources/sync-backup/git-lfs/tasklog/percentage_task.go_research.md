<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/percentage_task.go -->
# sources/sync-backup/git-lfs/tasklog/percentage_task.go

Purpose: implements `PercentageTask`, a throttled progress task for work with a known total.

Important APIs/types/functions: `PercentageTask`, `NewPercentageTask`, `Count`, `Entry`, `Complete`, `Updates`, and `Throttled`.

Control flow: constructor initializes a buffered channel and emits an initial zero-count update. `Count` atomically increments completed count, panics if it exceeds total, computes floored percentage (100 percent for total zero), sends a formatted update, and closes the channel when complete. `Entry` sends a forced line-delimited update. `Complete` atomically sets count to total and closes the channel if not already complete.

State and persistence: uses atomic `n`, immutable `total`, task message, and update channel. No persistent storage.

Dependencies and integration points: depends on `sync/atomic`, translation package `tr`, and the shared `Task`/`Update` logger contract. Created by `Logger.Percentage`.

Risks: callers must not call `Count` after the channel closes or over-count; both can panic. Forced entries can block on the one-slot channel without an active consumer.

Test signals: `percentage_task_test.go` covers percentage formatting, zero-total behavior, completion closure, throttled flag, and overcount panic.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/percentage_task.go -->
