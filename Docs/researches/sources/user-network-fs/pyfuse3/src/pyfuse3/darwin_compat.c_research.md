# sources/user-network-fs/pyfuse3/src/pyfuse3/darwin_compat.c

Purpose: Implements a POSIX-semaphore compatibility layer for Darwin using pthread mutexes and condition variables, because unnamed POSIX semaphores are not available the same way on macOS.

Important APIs/types/functions: Implements `darwin_sem_init`, `darwin_sem_destroy`, `darwin_sem_getvalue`, `darwin_sem_post`, `darwin_sem_timedwait`, `darwin_sem_trywait`, and `darwin_sem_wait`. Internal sentinel ids `__SEM_ID_NONE` and `__SEM_ID_LOCAL` validate initialization state.

Control flow: Initialization creates a condition variable and mutex, sets count, then marks the semaphore local. Wait paths lock the mutex, validate id, block on the condition when count is zero, decrement count on success, and unlock using pthread cleanup handlers. Post increments count and signals waiters when transitioning from zero.

State and persistence: State lives in `darwin_sem_t`: id, count, mutex, and condition variable. It is in-memory synchronization state only.

Dependencies and integration points: Includes `darwin_compat.h`, `pthread`, `errno`, and `assert`. It is compiled into pyfuse3 only on Darwin by `util/build_backend.py` and is exposed through macro aliases in the header.

Risks: `darwin_sem_wait` treats a spurious wake with no count as `EINTR`; repeated spurious wakes can surface as errors. `darwin_sem_destroy` broadcasts while destroying and must not race with active users. Timed wait asserts non-timeout pthread errors as impossible.

Test signals: No direct unit tests. Darwin builds and runtime FUSE operations indirectly validate semaphore behavior.
