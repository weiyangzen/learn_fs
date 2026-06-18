<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/simple_task.go -->
# sources/sync-backup/git-lfs/tasklog/simple_task.go

Purpose: implements `SimpleTask`, an unthrottled task that emits arbitrary formatted strings and blocks completion until the logger acknowledges it.

Important APIs/types/functions: `SimpleTask`, `NewSimpleTask`, `Log`, `Logf`, `Complete`, `OnComplete`, `Updates`, and `Throttled`.

Control flow: `Log` delegates to `Logf`; `Logf` sends an update with formatted text. `Complete` adds one waitgroup count, closes the channel, and waits. `Logger.logTask` detects `OnComplete` and calls it after consuming all updates, which releases `Complete`.

State and persistence: in-memory unbuffered channel and wait group. No disk state.

Dependencies and integration points: relies on `Logger.logTask` optional `OnComplete` callback; created by `Logger.Simple`.

Risks: `Complete` blocks forever if no logger or consumer calls `OnComplete`. Calling `Log` without a consumer also blocks because the channel is unbuffered.

Test signals: `simple_task_test.go` covers logging, formatted logging, closure/completion acknowledgement, and unthrottled flag.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/simple_task.go -->
