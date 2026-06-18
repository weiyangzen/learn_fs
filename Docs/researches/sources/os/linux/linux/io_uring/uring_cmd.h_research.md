# File Research: sources/os/linux/linux/io_uring/uring_cmd.h

Header for io_uring passthrough command support.

Key responsibilities:
- Defines `struct io_async_cmd`, containing reusable vector storage and up to two SQE slots for 128-byte commands.
- Declares uring_cmd prep, issue, SQE copy, cleanup, cancellation, multishot CQE32, cache-free, and poll-multishot helpers.

Important invariant:
- `sqes[2]` is sized to hold one normal SQE or one SQE128 command copy.
