# sources/test-tools/liburing/test/sq-full.c

Purpose: verifies `io_uring_get_sqe()` returns exactly the queue depth worth of SQEs and then reports full.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_get_sqe`, and `io_uring_queue_exit`.

Control flow: creates an 8-entry ring, loops until `io_uring_get_sqe()` returns NULL, counts acquired SQEs, and fails unless the count is 8.

State/persistence behavior: no persistent state; it only consumes local SQ slots without submitting them.

Dependencies/integration: baseline liburing queue accounting test.

Risks/test signals: detects off-by-one SQ capacity bugs or get-SQE behavior that allows overfill/underfill.
