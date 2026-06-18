# sources/test-tools/liburing/test/recv-inc-ooo.c

Purpose: verifies ordering for multishot receive with receive bundles and incrementally consumed provided buffers. It targets a reported issue where incremental buffer consumption could place received data out of order.

Important APIs and types: `io_uring_register_buf_ring` with `IOU_PBUF_RING_INC`, `io_uring_prep_recv_multishot`, `IORING_RECVSEND_BUNDLE`, `IOSQE_BUFFER_SELECT`, mmap-backed buffer memory, socket-pair helper, and ring setup flags for defer-taskrun, SQPOLL, and cooperative task-run.

Control flow: `setup_buf_ring()` maps a four-entry 1024-byte buffer area, registers it as an incremental buffer ring, and publishes all entries. `test_recv_incr()` creates a stream socket pair, submits one bundled multishot recv, then writes 2 KiB of patterned data in deliberately uneven chunks: 512, 333, 777, and 426 bytes. For each chunk, it waits until the whole chunk has been received. `process_completion()` checks each CQE result, validates the bytes at the current incremental cursor, and advances `rb.cursor` by `cqe->res`.

State and persistence: `struct read_buf` tracks the user-space view of the incremental consumption cursor. `data_received` is local to the test. The kernel's incremental buffer tail persists across all completions and is checked by reading from `buffer_memory + cursor`.

Dependencies and integration: requires buffer-ring incremental support and recv multishot. Unsupported `-EINVAL` marks skip. The same scenario is run under several ring setup modes after the baseline succeeds.

Risks and test signals: failures indicate data ordering corruption, incorrect incremental cursor advancement, unsupported feature handling regressions, or incomplete receive. Passing shows uneven stream chunks are laid out sequentially in the incremental buffer across bundled multishot completions.
