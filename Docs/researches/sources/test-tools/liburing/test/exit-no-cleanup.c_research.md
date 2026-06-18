<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/exit-no-cleanup.c -->
## sources/test-tools/liburing/test/exit-no-cleanup.c

Purpose: stress test for process exit while many threads own rings with pending io-wq-backed reads and no explicit cleanup.

Important APIs/types/functions: `pthread_create`, `pthread_barrier_t`, `sem_t`, `pipe`, `io_uring_queue_init`, `io_uring_prep_read`, `io_uring_submit_and_wait`, and sanitizer guard `CONFIG_USE_SANITIZER`.

Control flow: when sanitizer builds are not enabled, `main` creates one thread per CPU, each thread creates a ring and loops reading from a shared pipe. The parent writes one notification per CPU, waits until each thread reports a completed read, then calls `exit` without joining threads or exiting rings.

State and persistence behavior: global thread array, barrier, semaphore, and pipe descriptors coordinate worker startup and completion. The deliberate persistence behavior is leaked live rings and threads at process exit.

Dependencies and integration points: targets io-wq cleanup, task exit, pthread interaction, and ASAN-unsafe timing.

Risks: highly timing and CPU-count dependent. It is skipped under sanitizer builds to avoid known unrelated cleanup crashes.

Test signals: pass is a clean process exit after leaving active rings uncleaned.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/exit-no-cleanup.c -->
