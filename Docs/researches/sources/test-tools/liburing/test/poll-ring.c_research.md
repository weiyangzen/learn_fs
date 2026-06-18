# sources/test-tools/liburing/test/poll-ring.c

Purpose: minimal regression test for polling an io_uring ring fd from the same ring, which can create circular references during process exit.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_prep_poll_add`, `io_uring_sqe_set_data`, `ring.ring_fd`, and `POLLIN`.

Control flow: creates a one-entry ring, queues a poll add on `ring.ring_fd`, submits it, and exits without explicitly draining or tearing the ring down.

State and persistence behavior: intentionally leaves an in-flight poll on the ring fd so process cleanup exercises reference release. No files.

Dependencies and integration points: depends on kernel ring-fd poll support and process-exit cleanup paths.

Risks and test signals: direct process return is success; external harnesses detect buggy kernels by stuck worker references or hung exit after the circular poll.
