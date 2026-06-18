# sources/test-tools/liburing/examples/poll-bench.c

## sources/test-tools/liburing/examples/poll-bench.c

Purpose: Microbenchmark for io_uring poll operations on registered pipe file descriptors.

Important APIs/functions: `io_uring_queue_init`, `io_uring_register_files`, `io_uring_register_ring_fd`, `io_uring_prep_poll_add`, `io_uring_submit`, `io_uring_wait_cqe`.

Control flow: create pipe, initialize ring with `SINGLE_ISSUER` fallback, register pipe fds and ring fd, then for 10 seconds repeatedly queue 32 fixed-file poll requests for `POLLIN`, submit, write/read one byte through the pipe to satisfy polls, consume 32 CQEs, and count completions.

State and persistence: pipe buffers and ring registrations only. No files.

Dependencies/integration: liburing poll support, registered files, POSIX pipe.

Risks: returns on first submit mismatch; no cleanup on failures; benchmark can be distorted by pipe/read/write overhead and by arming multiple polls on same fd.

Test signals: stderr `requests/s` throughput line and zero exit.
