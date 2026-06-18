# sources/test-tools/liburing/test/thread-exit.c

Purpose: regression test that io_uring work submitted by short-lived pthreads is not canceled merely because the submitting thread exits, while still relying on process/ring teardown to cancel long-lived work. It submits writes that should complete and poll requests that remain pending.

Important APIs/types/functions: `struct d`, global `g_buf`, `free_g_buf`, `do_io`, `pthread_create`, `pthread_join`, `pipe`, `t_create_file`, `io_uring_queue_init`, `io_uring_prep_write`, `io_uring_prep_poll_add`, `io_uring_submit`, and `io_uring_wait_cqe`.

Control flow: main creates a pipe and ring, opens either a user-provided file or `.thread.exit`, then starts and joins eight threads. Each thread allocates a write buffer, queues one write and one poll, submits both SQEs, and exits. Main then reaps exactly eight write CQEs and requires each result to equal `WSIZE`; it does not reap the sticky poll requests before process exit.

State/persistence behavior: writes 512-byte chunks at monotonically increasing offsets. Buffers are kept in `g_buf` until completions arrive so submitted write memory remains valid after thread exit. Temporary file cleanup is by unlink-after-open.

Dependencies/integration: depends on pthreads, pipes, regular-file writes, poll wait queues, liburing helpers, and kernel io-wq lifetime semantics.

Risks/test signals: skips on inaccessible target file. Failures show as missing CQEs, short write results, bad submit counts, or worker-side `d.err` increments. The shared `struct d` is safe only because each thread is joined before the next mutation.
