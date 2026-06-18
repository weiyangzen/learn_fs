# File Research: sources/os/linux/linux-stable/fs/timerfd.c

Purpose: Implements Linux timerfd file descriptors and syscalls for timer creation, arming, reading expirations, polling, fdinfo, checkpoint/restore tick injection, and 32-bit time compatibility.

Key responsibilities:
- Defines `timerfd_ctx`, wrapping either an hrtimer or alarmtimer.
- Implements expiration callbacks that increment ticks and wake poll/read waiters.
- Supports `CLOCK_MONOTONIC`, `CLOCK_REALTIME`, `CLOCK_BOOTTIME`, and realtime/boottime alarm clocks.
- Maintains a cancel-on-set list for absolute realtime timers with `TFD_TIMER_CANCEL_ON_SET`.
- Handles clock-set and resume notifications through `timerfd_clock_was_set()` and deferred work.
- Implements file operations: release, poll, read_iter, fdinfo, ioctl, and noseek.
- Implements `timerfd_create`, `timerfd_settime`, `timerfd_gettime`, and 32-bit time variants.
- Supports periodic timers by forwarding/restarting on read or gettime rather than from the timer callback.

Important interactions:
- Uses anon inodes, wait queues, hrtimer, alarmtimer, RCU, time namespaces, capabilities, and user-copy helpers.
- Alarm clocks require `CAP_WAKE_ALARM`.
- Checkpoint/restore can set nonzero ticks with `TFD_IOC_SET_TICKS`.

Notable invariants and risks:
- Cancel-on-set timers return `-ECANCELED` and clear ticks/expired state when realtime offset changes.
- Short-period periodic timers are rearmed from user access paths to avoid timer callback denial-of-service behavior.
- File descriptor validation checks `f_op == &timerfd_fops`.
