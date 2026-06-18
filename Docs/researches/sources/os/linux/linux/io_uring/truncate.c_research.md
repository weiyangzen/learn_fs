# File Research: sources/os/linux/linux/io_uring/truncate.c

io_uring ftruncate operation implementation.

Key responsibilities:
- Prepares ftruncate SQEs, accepting new length from `sqe->off`.
- Rejects unused SQE fields.
- Forces async execution.
- Executes `do_ftruncate()` on the request file and completes with its result.

Important invariants:
- Issue path expects blocking context and warns if invoked with nonblocking issue flags.
- Length is stored as `loff_t`; validation is delegated to `do_ftruncate()`.
