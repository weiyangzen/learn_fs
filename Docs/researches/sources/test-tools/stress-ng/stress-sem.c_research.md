# sources/test-tools/stress-ng/stress-sem.c

Purpose: implements the POSIX `sem` stressor, using pthreads to contend on a local or process-shared `sem_t` with `sem_trywait`, `sem_timedwait`, `sem_wait`, `sem_post`, and `sem_getvalue`.

Important APIs/types/functions: `stress_sem_init`, `stress_sem_deinit`, `stress_sem_thrash`, `stress_sem`, `stress_sem_pthread_t`, `sem_init`, `sem_destroy`, `sem_getvalue`, `sem_trywait`, `sem_timedwait`, `sem_wait`, `sem_post`, `pthread_create`, `pthread_cancel`, `pthread_join`, and `stress_mmap_populate`.

Control flow: global init maps and initializes a process-shared semaphore for `--sem-shared`. The worker chooses thread count from settings/minimize/maximize and chooses shared mode from settings/aggressive mode. It initializes a local semaphore when not shared, synchronizes start, spawns pthreads, lets them loop through trywait/timedwait/wait modes, and later cancels/joins all successful threads while aggregating per-thread call counters.

State and persistence behavior: local semaphore state is per worker and destroyed at exit; shared semaphore state is a MAP_SHARED anonymous mapping named `shared-semaphore` and destroyed/unmapped by deinit. Each thread updates local metric counters and the common bogo counter after successful lock acquisition and post.

Dependencies and integration points: registered with init/deinit hooks, `CLASS_OS | CLASS_SCHEDULER | CLASS_IPC`, always verify, and `sem-procs`/`sem-shared` options. It depends on POSIX semaphores, pthread support, stress-ng mmap helpers, scheduler yielding, and global option flags.

Risks and test signals: failure modes include missing POSIX semaphore support, inability to allocate/init the shared semaphore, no threads created, unexpected semaphore API errors, and cancellation while updating bogo state. Test signals include nonzero call-rate metrics for each wait mode and successful cleanup of local or shared semaphores.
