# sources/storage-engines/wiredtiger/tools/tsan_playground/tsan_playground.c

Purpose: common concurrent workload used to compare how TSAN treats different atomic and barrier implementations.

Important APIs and control flow: compile-time macros select one API header. Shared state includes `message`, `pos`, and atomic `count`. `ping_pong()` waits until `count % NUM_THREADS` matches its thread id, writes one character into `message`, increments `pos`, prints a line, then release-stores `count + 1`. `main()` prints the implementation label, initializes shared state, starts four pthreads, and joins them.

State and persistence behavior: all state is process memory and stdout. No files or database state are written.

Dependencies and integration points: depends on pthreads and the selected atomic API header. Built as many executables by `CMakeLists.txt` and evaluated by `collect_warnings.sh`.

Risks: the workload relies on the counter creating a happens-before relationship for non-atomic `message` and `pos`; if the chosen implementation is not sanitizer-visible, TSAN reports races even if hardware ordering is intended. `printf` interleaves with shared message mutation and may add synchronization/noise. The character calculation can produce non-printable bytes after enough iterations, though `num_iters` is small.

Test signals: all variants should terminate; TSAN warnings distinguish recognized synchronization from dummy or fence-only patterns.
