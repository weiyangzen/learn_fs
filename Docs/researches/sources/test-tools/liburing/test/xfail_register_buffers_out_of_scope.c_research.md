# sources/test-tools/liburing/test/xfail_register_buffers_out_of_scope.c

Purpose: negative ASan-oriented test for registering buffers after freeing one iovec base. It is intended to expose use-after-free detection in buffer registration paths.

Important APIs/types/functions: `calloc`, `malloc`, `free`, `io_uring_queue_init`, `io_uring_register_buffers`, `io_uring_submit_and_wait`, `struct iovec`, `BUFFERS`, and `BUFFER_SIZE`.

Control flow: main initializes a ring, allocates an array of eight iovecs and backing buffers, frees `iovs[4].iov_base`, calls `io_uring_register_buffers` with the stale pointer still present, then submits/waits and returns `T_EXIT_PASS`. Queue init failure is also treated as pass because the xfail uses inverted exit-code expectations.

State/persistence behavior: heap allocation state is intentionally corrupted by freeing one registered buffer candidate. No files or durable state.

Dependencies/integration: intended for sanitizer-instrumented liburing/kernel-test harnesses. It uses normal buffer registration but expects external tooling to flag invalid memory use.

Risks/test signals: exit status alone does not indicate the bug; without ASan or equivalent it may pass. Memory allocated for other buffers is not freed because process exit is the cleanup boundary.
