# File Research: sources/os/linux/linux/fs/proc/uptime.c

## Scope

This file implements `/proc/uptime`.

## Public And Internal APIs Covered

- Display callback: `uptime_proc_show()`.
- Init: `proc_uptime_init()`.

## Control Flow And Behavior

- `uptime_proc_show()` sums idle time across all possible CPUs using `get_idle_time()`.
- It fetches boottime uptime, applies the current time namespace boot offset, converts accumulated idle nanoseconds to seconds/nanoseconds, and emits both values with two decimal places.
- Init creates a permanent single-show proc entry named `uptime`.

## Dependencies And Risks

- Depends on `get_idle_time()` from `stat.c`, per-CPU cpustat fetch, boottime clock, and time namespace offsets.
- Idle time is accumulated over possible CPUs and can exceed wall-clock uptime on multicore systems.
