# sources/test-tools/liburing/test/ringbuf-status.c

Purpose: validates userspace-visible provided buffer ring status helpers, especially group head lookup and available count before and after consumption.

Important APIs/types/functions: `io_uring_buf_ring_head`, `io_uring_buf_ring_available`, `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, and group id `BGID`.

Control flow: `test(0)` initializes an 8-buffer ring, verifies head zero and all buffers available, queues a pipe read with buffer selection, confirms head unchanged before data arrives, writes data, waits for completion, and verifies head advanced and availability dropped. `test(1)` checks invalid group-id lookup. `test_max()` registers 32,768 buffers and verifies availability at half and full states.

State/persistence behavior: all state is buffer-ring metadata, pipe data, and in-memory buffers. No files are persisted.

Dependencies/integration: requires kernel support for buffer rings and ring status queries; `-EINVAL` sets skip flags for missing support. It uses pipes to create a controlled buffer consumption event.

Risks/test signals: catches incorrect head reporting, bad invalid-group behavior, wrong availability counts, and missing buffer-selection completions. The high-buffer-count case also exercises sizing/overflow boundaries.
