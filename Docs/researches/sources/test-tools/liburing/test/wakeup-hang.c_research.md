# sources/test-tools/liburing/test/wakeup-hang.c

Purpose: regression test that poll requests sleeping in io_uring wake correctly when signaled by pipe and eventfd writes, avoiding hangs in wakeup paths.

Important APIs/types/functions: `struct thread_data`, `listener_thread`, `wakeup_io_uring`, `test_pipes`, `test_eventfd`, `io_uring_prep_poll_add`, `io_uring_wait_cqe`, `eventfd`, `eventfd_write`, `pipe`, pthreads, and `POLLIN`.

Control flow: `test_pipes` creates a pipe, queues a poll-add on the read end, starts a listener thread blocked in `io_uring_wait_cqe`, sleeps one second, and starts a writer thread that writes to the pipe write end using `eventfd_write`-style helper data. `test_eventfd` repeats the pattern with an actual eventfd. Main requires both listener joins to report success.

State/persistence behavior: only file descriptor readiness state and ring CQ state exist. Descriptors are closed by process teardown; rings are explicitly exited.

Dependencies/integration: exercises io_uring poll wait queues, eventfd/pipe readiness, pthread scheduling, and CQ wakeups.

Risks/test signals: can hang if wakeup is broken because no timeout guard is installed. Failures include wait errors, negative CQE results, failed submit, or listener thread returning an error pointer.
