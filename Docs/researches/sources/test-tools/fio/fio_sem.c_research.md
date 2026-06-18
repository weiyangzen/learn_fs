# sources/test-tools/fio/fio_sem.c

Purpose: implements fio's small counting semaphore abstraction on top of a process-shared pthread mutex and condition variable. It supports mmap-backed semaphores, inline initialization for embedded/shared objects, blocking waits, timed waits, trylock, wakeups, and removal.

Important APIs/types/functions: exports `__fio_sem_init`, `fio_sem_init`, `__fio_sem_remove`, `fio_sem_remove`, `fio_sem_down_timeout`, `fio_sem_down_trylock`, `fio_sem_down`, and `fio_sem_up`. Internal `sem_timed_out` compensates for platforms whose timed condition wait may return timeout early.

Control flow: `fio_sem_init` allocates `struct fio_sem` with anonymous shared mmap and calls `__fio_sem_init`; failure removes/unmaps. `fio_sem_down` locks the mutex, waits while `value` is zero, tracks waiters around each `pthread_cond_wait`, decrements value, and unlocks. The timeout variant computes an absolute timeout using monotonic clock when supported, loops on `pthread_cond_timedwait`, double-checks elapsed wall time after `ETIMEDOUT`, and decrements only on success. `fio_sem_up` increments value and signals one waiter if the semaphore was previously unavailable and waiters exist.

State and persistence behavior: semaphore state is in `value`, `waiters`, `magic`, `pthread_mutex_t`, and `pthread_cond_t`. `__fio_sem_remove` destroys pthread objects and clears memory outside Valgrind so use-after-remove tends to assert on magic rather than hang. `fio_sem_remove` additionally unmaps mmap storage.

Dependencies/integration: depends on `fio_sem.h`, `pshared.h` for `mutex_cond_init_pshared`, `os/os.h` for mmap flags, `fio_time.h`/`gettime.h` for timeout math, pthreads, mmap, and Valgrind detection. Used by flow control, gettimeofday thread startup, job synchronization, and file locks.

Risks and test signals: `fio_sem_down_trylock` returns `false` on successful acquisition and `true` when unavailable, which is easy to misuse. Timed waits rely on correct condition-variable clock attributes from `pshared`. Test signals should cover interprocess use, embedded `__fio_sem_init`/`__fio_sem_remove`, timeout accuracy, trylock semantics, wake-one behavior, removal while unused, and Valgrind/non-Valgrind behavior.
