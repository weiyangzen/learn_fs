<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/log_test.go -->
# sources/sync-backup/git-lfs/tasklog/log_test.go

Purpose: unit tests for `Logger` sequencing, throttling, progress suppression, helper constructors, and nil handling.

Important APIs/types/functions: defines test `ChanTask` and `UnthrottledChanTask`; tests `NewLogger`, `ForceProgress`, `Enqueue`, `Close`, `Waiter`, `Percentage`, `List`, `Simple`, and logger internals such as throttle/width overrides.

Control flow: tests feed update channels through the logger and compare exact sink output. They validate multiple tasks run in order but enqueue does not block indefinitely, throttled updates are skipped except forced/last lines, unthrottled tasks log all updates, silent tasks print nothing, and constructors enqueue typed tasks.

State and persistence: in-memory channels and buffers only.

Dependencies and integration points: uses `testify/assert`; validates output consumed by command-line progress users.

Risks: exact string expectations couple tests to carriage-return and padding semantics. Timing tests use synthetic timestamps, avoiding real-time flakes.

Test signals: covers progress output with and without forced progress, task ordering, throttling edge cases, durable updates, silent tasks, helper methods, nil logger enqueue draining, and nil close.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/log_test.go -->
