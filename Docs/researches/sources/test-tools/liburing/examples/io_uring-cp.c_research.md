# sources/test-tools/liburing/examples/io_uring-cp.c

## sources/test-tools/liburing/examples/io_uring-cp.c

Purpose: Asynchronous file/block-device copy example using separate read and write SQEs, bounded queue depth, and short I/O repair.

Important APIs/types/functions: `struct io_data` carries operation state, offsets, first length, and iovec; `get_file_size`; `queue_read`, `queue_write`, `queue_prepped`; `copy_file`; `io_uring_prep_readv`, `io_uring_prep_writev`.

Control flow: main opens input/output, initializes ring, determines input size, and calls `copy_file`. The copy loop fills queue with reads up to `QD`, submits, waits/peeks completions, retries `-EAGAIN`, adjusts short reads/writes by moving iov base/len and offset, turns completed reads into writes, frees data after write completion, then drains pending writes.

State and persistence: writes output file, uses heap allocation per chunk with payload after metadata. Global `infd/outfd` simplify callbacks.

Dependencies/integration: relies on regular or block-device input, `BLKGETSIZE64`, liburing, and POSIX file APIs.

Risks: pointer arithmetic on `void *` is GNU C extension. Error exits can leak queued buffers. Output file permissions fixed at 0644. Does not preserve metadata or sparse extents.

Test signals: output equality can be externally compared; internal errors print CQE failures or short submit failures.
