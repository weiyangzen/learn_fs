<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/task.go -->
# sources/sync-backup/git-lfs/tasklog/task.go

Purpose: defines the common tasklog interfaces and update payload used by all task implementations.

Important APIs/types/functions: `Task` interface with `Updates() <-chan *Update` and `Throttled() bool`; `Update` struct with string, timestamp, and force flag; `Update.Throttled`.

Control flow: `Update.Throttled` compares the update timestamp with a supplied threshold and returns false for forced updates, enabling logger throttle decisions.

State and persistence: no persistent state; defines in-memory contracts.

Dependencies and integration points: consumed by `Logger`, `ListTask`, `PercentageTask`, `SimpleTask`, `WaitingTask`, and tests.

Risks: interface changes affect every progress task and command using tasklog. Throttle semantics must preserve forced updates for important messages.

Test signals: covered indirectly by logger and task-specific tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/task.go -->
