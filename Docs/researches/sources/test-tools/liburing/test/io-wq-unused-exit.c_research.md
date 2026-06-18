<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/io-wq-unused-exit.c -->
## sources/test-tools/liburing/test/io-wq-unused-exit.c

Purpose: ensures io-wq worker threads disappear after the last ring is closed, supporting checkpoint/restore style quiescence.

Important APIs/types/functions: `count_iowq_workers`, `wait_for_iowq_workers`, `/proc/self/task/*/comm`, `io_uring_prep_splice`, `io_uring_queue_exit`, and helper timing `mtime_since_now`.

Control flow: the test creates a ring, temporary source/destination files, a pipe, submits two splice operations, validates both completions, waits until at least one `iou-wrk-` thread is visible, exits the ring, then waits up to two seconds for all such worker threads to disappear.

State and persistence behavior: worker-thread presence is observed through procfs task comm names. Temporary files and pipe fds are cleaned on all exit paths.

Dependencies and integration points: integrates io-wq creation by splice with ring shutdown and procfs worker detection.

Risks: if workers are not observed quickly, the test converts that failure to skip because the environment may not have created io-wq workers. Name-prefix matching depends on kernel worker naming.

Test signals: pass means io-wq worker threads are not left lingering after ring closure.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/io-wq-unused-exit.c -->
