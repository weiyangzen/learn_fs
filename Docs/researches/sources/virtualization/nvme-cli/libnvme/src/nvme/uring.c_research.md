# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/uring.c

## Purpose
Implements asynchronous NVMe passthrough submission using `io_uring` and `IORING_OP_URING_CMD`.

## Main Logic
- Probes kernel support for `IORING_OP_URING_CMD`.
- Opens/closes an `io_uring` queue with SQE128/CQE32 setup and 16 entries.
- Wraps each async command in `struct libnvme_async_req`, preserving passthrough command, cookie, user data, opcode, and dry-run queue linkage.
- Submits admin and I/O passthrough via `LIBNVME_URING_CMD_ADMIN` or `LIBNVME_URING_CMD_IO`.
- Reaps completions, calls transport submit callbacks, handles retry decisions, and returns completion status/cookie.
- Supports dry-run mode by queueing requests internally and completing them without kernel submission.

## Error Handling
Returns `-ENODEV` for missing handles, `-ENOTSUP` when io_uring is unavailable, `-EAGAIN` for full queues or no completions, and propagates allocation/submission errors. Closing drains pending completions before freeing the ring.

## Relevance
This is the async command path for high-throughput NVMe passthrough operations, falling back elsewhere when unsupported.
