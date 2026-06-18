# File Research: sources/os/linux/linux/block/ioprio.c

Implements the `ioprio_set` and `ioprio_get` syscalls for per-task I/O priority.

Key responsibilities:
- Validates I/O priority class and level.
- Requires `CAP_SYS_ADMIN` or `CAP_SYS_NICE` for realtime I/O priority.
- Supports process, process group, and user selection modes.
- Returns raw priority for single-process lookup to preserve historical behavior.
- Returns the best priority across process-group or user queries.

Important functions:
- `ioprio_check_cap()` validates class/level and privilege.
- `SYSCALL_DEFINE3(ioprio_set)` applies priority to selected tasks.
- `get_task_ioprio()` enforces LSM checks and returns effective task priority.
- `get_task_raw_ioprio()` returns explicitly stored task I/O priority or default.
- `SYSCALL_DEFINE2(ioprio_get)` queries selected tasks.

Concurrency/lifetime notes:
- Uses RCU while locating tasks/users/process groups.
- Uses `tasklist_lock` for process-group iteration.
- Uses `task_lock()` around task I/O context access.
- Calls `security_task_getioprio()` for LSM mediation.

Research relevance:
- This provides the userspace policy input consumed by schedulers such as `mq-deadline`.
