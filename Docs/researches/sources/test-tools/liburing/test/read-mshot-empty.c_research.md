# sources/test-tools/liburing/test/read-mshot-empty.c

Purpose: verifies multishot reads continue draining available data even when a pipe has more bytes than one provided buffer can hold. It targets an implementation bug where multishot read stopped too early if available data exceeded buffer size.

Important APIs and types: `io_uring_setup_buf_ring`, `io_uring_prep_read_multishot`, `IORING_CQE_F_BUFFER`, `IORING_CQE_F_MORE`, buffer IDs encoded in `cqe->flags`, `pthread_create`, and pipe read/write APIs. Four 32-byte buffers are registered in a buffer ring.

Control flow: a writer thread writes two 32-byte blocks, sleeps briefly, then writes two more. The main thread creates a pipe and ring, registers four buffers, submits one `io_uring_prep_read_multishot()` on the pipe read end, checks for immediate `-EINVAL` or `-EBADF` unsupported CQE, starts the writer, and waits for four CQEs. Each CQE must be 32 bytes, have a selected buffer, and carry `IORING_CQE_F_MORE`.

State and persistence: the multishot read request persists across multiple pipe writes and multiple buffer selections. Buffer ring entries are consumed by the kernel; the test does not recycle them because exactly four buffers match the four expected completions.

Dependencies and integration: requires multishot read and buffer ring support. Unsupported operation is detected by peeking after submission and returning skip.

Risks and test signals: failures indicate early termination, missing `MORE`, missing selected buffer flag, or incorrect lengths. Passing shows one multishot read can span multiple readiness episodes and drain all four buffers.
