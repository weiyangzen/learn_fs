<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fifo-futex-poll.c -->
## sources/test-tools/liburing/test/fifo-futex-poll.c

Purpose: ensures an inline-failing futex wait does not poison later fixed-file poll on a FIFO.

Important APIs/types/functions: `mkfifo`, `io_uring_prep_futex_wait`, `io_uring_register_files`, `io_uring_prep_poll_add`, `IOSQE_FIXED_FILE`, `FUTEX_BITSET_MATCH_ANY`, and `FUTEX2_SIZE_U32`.

Control flow: the test creates and opens a FIFO, initializes a ring, submits an invalid futex wait with a null address and expects `-EFAULT` or skips on `-EINVAL`. It then registers the FIFO fd, submits a fixed-file poll for `POLLIN`, writes to the FIFO, and waits for the poll completion.

State and persistence behavior: temporary `fifo` filesystem node and fifo fd are cleaned up; the ring holds one registered file during poll.

Dependencies and integration points: combines futex opcode validation with double-waitqueue FIFO poll and fixed-file registration.

Risks: stale local `fifo` path could interfere. Unsupported futex opcode maps to skip.

Test signals: pass means a failed futex SQE does not corrupt later poll request setup or completion.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fifo-futex-poll.c -->
