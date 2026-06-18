# File Research: sources/os/linux/linux/fs/proc/loadavg.c

## Scope

This file implements `/proc/loadavg`.

## Public And Internal APIs Covered

- Display callback: `loadavg_proc_show()`.
- Init: `proc_loadavg_init()`.

## Control Flow And Behavior

- `loadavg_proc_show()` fetches the 1, 5, and 15 minute load averages with `get_avenrun()`.
- It formats the traditional five fields: three load averages, runnable threads over total threads, and the last allocated PID cursor in the current task active PID namespace.
- Init creates a permanent single-show proc entry named `loadavg`.

## Dependencies And Risks

- Depends on scheduler load average, runnable/thread counters, and PID namespace IDR cursor state.
- Output is namespace-sensitive for the PID cursor through `task_active_pid_ns(current)`.
