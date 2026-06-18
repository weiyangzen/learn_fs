<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fdinfo-sqpoll.c -->
## sources/test-tools/liburing/test/fdinfo-sqpoll.c

Purpose: races `/proc/self/fdinfo/<ring_fd>` reads against SQPOLL ring teardown and signal interruption.

Important APIs/types/functions: `struct data`, `fdinfo_read`, `__test`, `test`, `t_create_ring(... IORING_SETUP_SQPOLL)`, `pthread_barrier_t`, `fork`, `kill`, and `waitpid`.

Control flow: each iteration forks. The child creates an SQPOLL ring, starts a thread continuously reading ring fdinfo, waits a random short interval, signals the thread to stop, joins it, and exits. The parent may send SIGINT during the child's fdinfo activity, then waits. `main` repeats this 1000 times.

State and persistence behavior: shared `done` flag and barrier coordinate the fdinfo reader. Ring fdinfo is opened once and read repeatedly while the ring may be torn down.

Dependencies and integration points: depends on procfs fdinfo, SQPOLL permission, pthreads, and signal/process cleanup.

Risks: nondeterministic race coverage; it mainly catches kernel crashes, hangs, or fdinfo read errors.

Test signals: pass means repeated fdinfo reads are stable during SQPOLL exit races.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fdinfo-sqpoll.c -->
