<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io-wq-exit.c -->
## sources/test-tools/liburing/test/io-wq-exit.c

Purpose: verifies a thread that creates io-wq work can exit promptly without waiting for idle worker timeout.

Important APIs/types/functions: thread function `test`, `get_time_ns`, `pthread_create`, `pthread_join`, `io_uring_prep_splice`, `pipe`, and `io_uring_queue_exit`.

Control flow: the worker thread creates a ring, source/destination files, and a pipe, writes source data, queues two splice operations through the pipe, waits for both completions, cleans resources, and exits. `main` measures total thread lifetime and fails if it takes 500 ms or more.

State and persistence behavior: temporary `.splice.<pid>.src` and `.splice.<pid>.dst` files plus pipe descriptors are created inside the thread and unlinked in cleanup.

Dependencies and integration points: targets io-wq worker lifecycle for splice operations and thread teardown.

Risks: timing threshold may be noisy on overloaded systems. There is a minor cleanup typo checking `fd_src` before closing `fd_dst`.

Test signals: pass means io-wq workers do not force long idle timeout waits during thread/ring exit.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io-wq-exit.c -->
