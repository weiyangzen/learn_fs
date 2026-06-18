<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fifo-nonblock-read.c -->
## sources/test-tools/liburing/test/fifo-nonblock-read.c

Purpose: regression test for retrying io_uring reads on nonblocking pipe/FIFO-style fds instead of returning immediate `-EAGAIN`.

Important APIs/types/functions: `pipe`, `t_set_nonblock`, `io_uring_prep_read`, `io_uring_submit`, `io_uring_wait_cqe`.

Control flow: a ring and pipe are created, the read end is made nonblocking, and a read SQE is submitted before data exists. After a short sleep, the write end receives data, and the test waits for a CQE whose result must be nonnegative.

State and persistence behavior: the pipe's nonblocking flag and pending read request are the relevant state. The ring is exited at the end.

Dependencies and integration points: exercises io-wq retry logic for nonblocking read endpoints.

Risks: the test accepts any nonnegative result and does not verify exact byte count. It assumes the delayed write races with the pending read as intended.

Test signals: pass means the kernel retries the operation until data arrives rather than reporting `-EAGAIN` to userspace.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fifo-nonblock-read.c -->
