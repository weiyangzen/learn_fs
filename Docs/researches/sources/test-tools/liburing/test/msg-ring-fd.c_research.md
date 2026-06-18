# sources/test-tools/liburing/test/msg-ring-fd.c

Purpose: tests `IORING_OP_MSG_RING` fd passing between rings, both in-process and to a ring owned by another thread.

Important APIs/types/functions: `io_uring_prep_msg_ring_fd`, `io_uring_register_files`, `io_uring_unregister_files`, `io_uring_prep_read`, `io_uring_prep_write`, `IOSQE_FIXED_FILE`, pthread barriers, and `IORING_SETUP_SINGLE_ISSUER | IORING_SETUP_DEFER_TASKRUN`.

Control flow: local mode registers fixed-file tables in source and destination rings, writes random bytes to a pipe, passes the read end into the destination fixed table, then reads via `IOSQE_FIXED_FILE` and compares buffers. Remote mode starts a thread with its own ring and performs the same fd handoff/read flow.

State and persistence behavior: transient pipes, registered fixed-file tables, and thread-shared buffer state. No filesystem persistence.

Dependencies and integration points: depends on sparse/fixed file support, msg-ring fd passing support, pthread synchronization, and normal/deferred ring modes.

Risks and test signals: `-EINVAL` can mark fd passing unsupported and skip. Failures include bad registration, message CQE errors, short reads/writes, or buffer mismatch after transfer.
