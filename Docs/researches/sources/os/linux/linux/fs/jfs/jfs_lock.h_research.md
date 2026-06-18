# File Research: sources/os/linux/linux/fs/jfs/jfs_lock.h

## Role

Provides a JFS wait helper for sleeping on a condition protected by an external spinlock.

## Key Responsibilities

- Includes Linux spinlock, mutex, and scheduler headers needed by lock/wait code.
- Defines `__SLEEP_COND(wq, cond, lock_cmd, unlock_cmd)`.
- Adds the current task to a wait queue, sets `TASK_UNINTERRUPTIBLE`, checks the condition while the caller's lock is held, drops the lock around `io_schedule()`, reacquires it, and removes the waiter after wakeup.

## Important Interactions

- The macro is parameterized with caller-provided lock and unlock commands so it can be used with different spinlock instances.
- Intended for code where the condition is protected by a spinlock but waiting must happen without holding that spinlock.

## Invariants and Risks

- Sleep is uninterruptible; callers must use it only where signal interruption is not required.
- The condition must be tested while the caller's lock is held.
- The wait queue entry is stack-allocated and must be removed before macro exit, which this macro does after setting the task back to running.
