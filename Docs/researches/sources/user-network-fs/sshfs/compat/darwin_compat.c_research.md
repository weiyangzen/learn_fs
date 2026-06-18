# sources/user-network-fs/sshfs/compat/darwin_compat.c

Purpose: provides a pthread-based POSIX semaphore compatibility layer for Darwin/macOS builds.

Important APIs/types/functions: `darwin_sem_init`, `darwin_sem_destroy`, `darwin_sem_getvalue`, `darwin_sem_post`, `darwin_sem_timedwait`, `darwin_sem_trywait`, and `darwin_sem_wait`.

Control flow: initialization rejects process-shared semaphores, initializes condition variable and mutex, stores count and an internal ID. Wait operations lock, validate ID, wait on the condition if count is zero, decrement on success, and use cleanup handlers to unlock. Post increments and signals on transition to one. Destroy marks invalid, broadcasts, destroys cond/mutex.

State and persistence behavior: semaphore state is embedded in `darwin_sem_t`; no global state.

Dependencies and integration points: used on Apple builds through macros in `darwin_compat.h`; `sshfs.c` uses `sem_t` for request completion.

Risks: `sem_wait` treats a spurious wakeup with zero count as `EINTR` instead of looping, which differs from normal semaphore semantics. Destroy while waiters exist is delicate. `sem_timedwait` asserts non-timeout errors from pthread condition wait.

Test signals: macOS build and concurrency tests for wait/post, trywait, timedwait timeout, destroy wakeups, and spurious wake tolerance.
