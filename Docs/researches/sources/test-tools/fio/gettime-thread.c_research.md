# sources/test-tools/fio/gettime-thread.c

Purpose: implements fio's optional gettimeofday offload thread, which continuously updates a shared timestamp so worker threads can read time through a seqlock without making system calls.

Important APIs/types/functions: defines global `struct fio_ts *fio_ts`, global `int fio_gtod_offload`, static `gtod_thread` and CPU mask, and exports `fio_gtod_init`, `fio_start_gtod_thread`, and `fio_gtod_set_cpu`. Internal functions are `fio_gtod_update` and `gtod_thread_main`.

Control flow: `fio_gtod_init` allocates shared timestamp storage once. `fio_start_gtod_thread` creates a locked startup semaphore, starts a small-stack detached thread, waits until the thread has attempted affinity setup, removes the semaphore, and returns creation/affinity status. The thread sets CPU affinity, signals startup, then loops while `nr_segments` is nonzero, calling `gettimeofday`, publishing the `timespec` under a seqlock, and executing `nop` to keep precision high. `fio_gtod_set_cpu` updates the target mask when CPU affinity is available.

State and persistence behavior: shared state is `fio_ts->ts` protected by `fio_ts->seqlock`, the offload flag, thread id, CPU mask, and the global `nr_segments` lifetime condition. No disk persistence.

Dependencies/integration: depends on `fio.h`, `lib/seqlock.h`, `smalloc`, `fio_sem`, CPU affinity OS helpers, and `gettimeofday`. `gettime.h` reads this state through `fio_gettime_offload`.

Risks and test signals: the update loop intentionally busy-spins and can consume a CPU; affinity failure aborts the thread; lifetime depends on `nr_segments`; and seqlock initialization must be valid in the `smalloc` allocation. Test signals should cover offload enabled/disabled, CPU pinning, startup synchronization, timestamp monotonicity enough for fio's use, and shutdown when segments drain.
