# sources/test-tools/liburing/test/rw_merge_test.c

Purpose: regression for incorrect async-list `io_should_merge()` behavior where a later file read could be merged with a blocked pipe read and hang.

Important APIs/types/functions: `io_uring_prep_readv`, `io_uring_wait_cqe_timeout`, `struct __kernel_timespec`, pipes, temporary file creation/truncation, and `t_create_ring`.

Control flow: queues a blocking pipe `readv` and a file `readv` past EOF, expects the file read CQE with result zero, then queues another file read adjacent to the previous file range. A three-second timeout detects whether the third read incorrectly merged with the pipe request and got stuck.

State/persistence behavior: creates and unlinks `testfile` while holding an fd, creates one pipe, and uses one shared buffer. The key state is kernel async request merge bookkeeping.

Dependencies/integration: relies on a kernel path that can punt reads to async context and on timeout waiting support. It skips only when ring creation is unavailable.

Risks/test signals: failure is a timeout or wrong CQE result/user data. The test uses assertions heavily, so abnormal behavior aborts rather than graceful diagnostics.
