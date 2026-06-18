# sources/test-tools/liburing/examples/io_uring-test.c

## sources/test-tools/liburing/examples/io_uring-test.c

Purpose: Minimal direct-I/O read demonstration for setting up a ring, submitting readv operations, consuming completions, and tearing down.

Important APIs/functions: `io_uring_queue_init`, `io_uring_get_sqe`, `io_uring_prep_readv`, `io_uring_submit`, `io_uring_wait_cqe`, `io_uring_cqe_seen`, `io_uring_queue_exit`.

Control flow: open file with `O_DIRECT`, stat size, allocate four 4096-byte aligned buffers, queue reads until queue or file exhausted, submit, wait for completions, validate full 4096-byte chunks except final file-sized remainder, print summary, free buffers and exit.

State and persistence: reads from input file only. Allocates and frees iovec buffers.

Dependencies/integration: depends on filesystem supporting `O_DIRECT`, aligned 4 KiB buffers, and liburing.

Risks: small or unaligned files/filesystems can produce direct-I/O errors. No handling for short non-final reads beyond failing. It does not check `calloc` return.

Test signals: successful summary output and zero exit; direct I/O failures expose environment limitations.
