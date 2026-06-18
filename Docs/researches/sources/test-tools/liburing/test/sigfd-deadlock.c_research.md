# sources/test-tools/liburing/test/sigfd-deadlock.c

Purpose: regression for signalfd polling deadlock involving recursive `sighand->siglock` acquisition.

Important APIs/types/functions: `sigprocmask`, `signalfd`, `io_uring_prep_poll_add`, `POLLIN`, `kill(getpid(), SIGINT)`, and `IORING_OP_POLL_ADD` completion masks.

Control flow: blocks SIGINT and creates a nonblocking signalfd, queues an io_uring poll for `POLLIN`, sends SIGINT to itself, waits for the poll CQE, and treats `-EOPNOTSUPP` as skip or `POLLIN` as pass.

State/persistence behavior: signal mask and signalfd readiness are process-local. No persistent data is touched.

Dependencies/integration: uses Linux signalfd and io_uring poll integration. It includes helper return codes for skip/pass/fail.

Risks/test signals: bad kernels can deadlock in poll wakeup or return wrong readiness/error. The test detects wrong masks and negative CQE results.
