# File Research: sources/os/linux/linux/fs/proc/array.c

## Purpose
Renders process and thread status/statistics text for procfs, especially `/proc/<pid>/status`, `/proc/<pid>/stat`, `/proc/<pid>/statm`, and optional `/proc/<pid>/task/<tid>/children`.

## Main Responsibilities
- Formats task names, states, IDs, credentials, groups, namespace PID views, and kernel-thread status.
- Renders signal pending/blocked/ignored/caught sets.
- Renders capabilities, seccomp state, speculation mitigation state, CPU masks, cpuset status, context switch counts, THP state, untag mask, and arch thread features.
- Emits the legacy fixed-field `/proc/<pid>/stat` and `/proc/<tid>/stat` formats.
- Emits `/proc/<pid>/statm` memory summary.
- Optionally emits first-level child PIDs when `CONFIG_PROC_CHILDREN` is enabled.

## Key Interfaces
- `proc_task_name()`
- `render_sigset_t()`
- `proc_pid_status()`
- `proc_tid_stat()`
- `proc_tgid_stat()`
- `proc_pid_statm()`
- `proc_tid_children_operations` under `CONFIG_PROC_CHILDREN`

## Control Flow and Data Handling
`proc_pid_status()` composes a multi-line human-readable status file. It obtains task memory via `get_task_mm()`, credentials via `get_task_cred()`, signal state under `lock_task_sighand()`, and namespace-aware IDs from pid namespace helpers.

`do_task_stat()` renders the legacy numeric stat line. It holds `exec_update_lock` while gathering sensitive execution fields, gates some fields behind `ptrace_may_access()`, and aggregates either thread-group-wide or per-thread counters. It intentionally masks or zeroes fields that are racy or sensitive.

The optional children seq file walks the task’s children under `tasklist_lock`, with comments documenting that the output is not perfectly race-free unless tasks are frozen.

## Dependencies and Integration
Depends on scheduler, signal, credential, pid namespace, time namespace, memory-management, cpuset, seccomp, ptrace, architecture, and procfs internals. `base.c` references these renderers in PID/TID entry tables.

## Concurrency and Lifetime Notes
The code uses RCU, task locks, sighand locks, `exec_update_lock`, seqlock reads for signal stats, and mm references. Many values are snapshots and can race with process exit or exec; the implementation prefers stable references and permission-gated fallbacks.

## Risks and Review Hotspots
- `/proc/<pid>/stat` field ordering is ABI-sensitive.
- Permission-gated address and wchan fields are security-sensitive.
- Namespace conversions must remain correct for nested PID/user namespaces.
- Children iteration explicitly trades precision for speed and should not be treated as an exact process-tree API.
