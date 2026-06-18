# sources/test-tools/liburing/test/poll-v-poll.c

Purpose: compares io_uring poll behavior against traditional `poll(2)` and `epoll_wait(2)` for pipes, regular files, and epoll file descriptors. It ensures io_uring reports readiness masks compatible with conventional readiness APIs and that `IORING_OP_EPOLL_CTL` can add an fd before polling the epoll instance.

Important APIs and types: `pthread_create`, `poll`, `epoll_create1`, `epoll_ctl`, `epoll_wait`, `io_uring_prep_poll_add`, `io_uring_prep_epoll_ctl`, `io_uring_submit`, and CQE wait/seen helpers. `struct thread_data` shares a ring, fd, event mask, and two output slots between worker threads.

Control flow: `iou_poll()` arms an io_uring poll and records `cqe->res & 0x3f`; `poll_pipe()` records `pfd.revents`; `epoll_wait_fn()` blocks on `epoll_wait`. Pipe `POLLIN` and `POLLOUT` tests start both io_uring and POSIX poll waiters, trigger readiness with a write, then compare masks. `do_test_epoll()` adds a pipe read end to an epoll fd either through `epoll_ctl` or through `io_uring_prep_epoll_ctl`, then verifies both io_uring poll and epoll waiter wake after data arrives. `do_fd_test()` compares readiness on a file opened from argv or the test binary.

State and persistence: readiness observations are transient and stored in `td.out`. The single-entry ring is shared by threads, so the test assumes serialized SQE use from its specific timing.

Dependencies and integration: requires pthreads, pipes, epoll, and liburing epoll-control support. If the io_uring epoll-control operation returns `-EINVAL`, that subcase is treated as unsupported and skipped internally.

Risks and test signals: mismatched masks between io_uring and POSIX readiness paths fail the test. Important coverage includes poll-on-epoll, both direct and io_uring-created epoll interest, and readiness of ordinary fds for `POLLIN`, `POLLOUT`, and both combined.
