# sources/test-tools/liburing/test/socket-rw-offset.c

Purpose: verifies socket `readv` with offset `-1` queued before a `writev` does not hang and completes correctly on kernels advertising current-position read/write support.

Important APIs/types/functions: TCP loopback setup, `IORING_FEAT_RW_CUR_POS`, `io_uring_prep_readv` with offset `-1`, `io_uring_prep_writev`, `io_uring_submit_and_wait`, and CQ iteration.

Control flow: creates a connected TCP pair, initializes a ring, skips if `IORING_FEAT_RW_CUR_POS` is absent, queues readv on one socket with offset `-1` and writev on the other, then waits until both CQEs report 128 bytes.

State/persistence behavior: socket data is transient; no filesystem persistence is involved.

Dependencies/integration: depends on feature bit semantics for offset `-1` on non-file fds and TCP loopback behavior.

Risks/test signals: detects hangs, wrong completion lengths, or improper offset handling for sockets.
