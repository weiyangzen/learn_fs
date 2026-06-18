# sources/sync-backup/kopia/internal/server/api_tasks.go

Purpose: exposes task manager state and controls through APIs.

Important APIs/types/functions: `handleTaskList`, `handleTaskInfo`, `handleTaskSummary`, `handleTaskLogs`, and `handleTaskCancel`.

Control flow: handlers read task lists, individual task info, summary counters, log text, or request task cancellation by ID from the server's `uitask.Manager`.

State and persistence behavior: reads and mutates task manager runtime state; persistent task logs depend on server `PersistentLogs` option.

Dependencies and integration points: used by UI to observe estimate, restore, repository connect, maintenance, and snapshot tasks.

Risks and test signals: cancellation must be idempotent and logs should not leak unrelated task data. Tests should cover missing task IDs, completed tasks, and cancellation propagation.
