# sources/test-tools/liburing/examples/io_uring-close-test.c

## sources/test-tools/liburing/examples/io_uring-close-test.c

Purpose: Demonstrates registering the io_uring ring fd and closing the original ring fd while continuing to submit I/O via the registered ring fd.

Important APIs/functions: `io_uring_queue_init`, `io_uring_register_ring_fd`, `io_uring_close_ring_fd`, `io_uring_prep_readv`, `io_uring_submit`, `io_uring_wait_cqe`, `io_uring_cqe_seen`.

Control flow: initialize ring, register and close ring fd, open input file, allocate four aligned 4 KiB buffers, queue readv requests up to file size, submit, wait for all completions, validate each is full-sized except final EOF chunk, print summary, close file and ring.

State and persistence: reads input file and allocates buffers. It leaks allocated iovec buffers and iovec array before exit, acceptable for short example but not reusable code.

Dependencies/integration: depends on liburing registered ring fd support and normal file I/O.

Risks: no cleanup on many early errors; no `O_DIRECT` but uses aligned buffers anyway; condition uses `offset > sb.st_size`, so exact-size boundary handling differs from `io_uring-test.c`. Demonstration assumes kernel supports ring fd registration.

Test signals: successful run prints submitted/completed/bytes and validates CQE byte counts.
