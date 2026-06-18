<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/list_task.go -->
# sources/sync-backup/git-lfs/tasklog/list_task.go

Purpose: implements `ListTask`, a tasklog task that emits unthrottled line-delimited entries and a final message.

Important APIs/types/functions: `type ListTask struct { msg string; ch chan *Update }`, `NewListTask`, `Entry`, `Complete`, `Throttled`, and `Updates`.

Control flow: constructor creates a buffered update channel. `Entry` sends an update string with a newline. `Complete` sends `<msg>: ...`, then closes the channel. `Throttled` returns false so the logger prints every update.

State and persistence: in-memory channel state only; no disk persistence. Completion closes the update channel and is a one-way state transition.

Dependencies and integration points: depends on `Update` and `Task` contracts in the same package and is enqueued by `Logger.List`.

Risks: sends can block if no logger/consumer drains the one-slot channel. Calling `Complete` multiple times would send/close on a closed channel.

Test signals: `list_task_test.go` covers completion update/closure, entry formatting, and unthrottled status.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tasklog/list_task.go -->
