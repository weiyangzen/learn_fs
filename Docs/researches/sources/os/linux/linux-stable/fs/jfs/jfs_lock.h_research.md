# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_lock.h

This header defines a small JFS locking/sleep helper for waiting on a condition protected by a spinlock.

Key responsibilities:
- Includes spinlock, mutex, and scheduler headers needed by JFS synchronization code.
- Defines `__SLEEP_COND(wq, cond, lock_cmd, unlock_cmd)`, which adds the current task to a wait queue, switches to `TASK_UNINTERRUPTIBLE`, drops the caller-provided lock while sleeping with `io_schedule()`, reacquires the lock, and exits when the condition becomes true.

Important interactions:
- Intended for JFS code paths where a wait condition is guarded by a spinlock and sleeping must temporarily release that lock.
- Uses caller-supplied lock/unlock command fragments rather than a typed lock object.

Notable invariants and risks:
- The macro sleeps uninterruptibly and requires the condition to become true or be woken by the relevant wait-queue protocol.
- Correctness depends on callers passing matching lock/unlock commands and holding the lock before entry.
- Because it is a macro with statement arguments, side effects in `cond`, `lock_cmd`, or `unlock_cmd` must be considered carefully.

Research notes:
- This is a low-level synchronization convenience header rather than a broad locking subsystem.
