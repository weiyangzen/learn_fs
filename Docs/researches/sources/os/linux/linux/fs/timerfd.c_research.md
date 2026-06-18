# File Research: sources/os/linux/linux/fs/timerfd.c

Purpose: Implements timerfd file descriptors and syscalls over hrtimer/alarmtimer.

Key syscalls and file operations:
- `timerfd_create(clockid, flags)`
- `timerfd_settime`, `timerfd_gettime`
- 32-bit time compat variants under `CONFIG_COMPAT_32BIT_TIME`
- File ops: release, poll, read_iter, noop llseek, proc fdinfo show, optional checkpoint/restore ioctl.

Implementation notes:
- `timerfd_ctx` stores hrtimer or alarm, interval, time namespace offset, waitqueue, tick count, clock id, cancel-on-set state, RCU node, and cancel-list linkage.
- Supports `CLOCK_MONOTONIC`, `CLOCK_REALTIME`, `CLOCK_BOOTTIME`, and realtime/boottime alarm clocks.
- Alarm clocks require `CAP_WAKE_ALARM`.
- `TFD_TIMER_CANCEL_ON_SET` absolute realtime timers are tracked in global RCU `cancel_list`; clock changes wake waiters and cause `-ECANCELED`.
- Periodic timers are rearmed lazily in read/gettime paths to avoid callback-side rearm abuse.

Concurrency and correctness:
- Waitqueue lock protects `ticks`, `expired`, timer rearm, and read/poll visibility.
- Separate `cancel_lock` protects per-context cancel-list membership; global `cancel_lock` protects the list.
- Release removes cancel-list membership, cancels hrtimer/alarm, then frees context with `kfree_rcu`.
- Settime loops with `try_to_cancel` plus `hrtimer_cancel_wait_running` to avoid reprogramming while callbacks run.
