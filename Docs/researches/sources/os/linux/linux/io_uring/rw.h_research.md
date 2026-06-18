# File Research: sources/os/linux/linux/io_uring/rw.h

Header for io_uring read/write async state and entry points.

Key responsibilities:
- Defines `struct io_async_rw`, including vector storage, bytes-done accounting, iterator state, fast iovec, buffer group, and the waitqueue/metadata union.
- Defines metadata retry state for PI/direct I/O.
- Declares prep and issue functions for read, write, vectored, fixed, vectored-fixed, and multishot read operations.
- Declares cleanup, failure, completion, and cache-free helpers.

Important invariants:
- `wpq` and metadata fields share storage and are mutually exclusive by operation mode.
- `bytes_done` is accumulated across partial retries and folded into final CQE result.
