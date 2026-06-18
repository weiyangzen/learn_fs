# sources/test-tools/liburing/test/msg-ring-flags.c

Purpose: validates msg-ring CQE injection with custom CQE flags through `io_uring_prep_msg_ring_cqe_flags()`.

Important APIs/types/functions: `send_msg`, `recv_msg`, `io_uring_prep_msg_ring_cqe_flags`, `CUSTOM_FLAG`, `USER_DATA`, `LEN`, pthread barrier, and deferred-taskrun ring setup.

Control flow: sends one message to a second local ring, verifies `user_data`, `res`, and `flags`, repeats eight sends/receives, then starts a destination ring in another thread and sends to it.

State and persistence behavior: only in-memory CQE delivery state across rings. No persistent resources beyond ring fds and a joined thread.

Dependencies and integration points: depends on msg-ring cqe-flags opcode support and ring flags 0 plus `SINGLE_ISSUER|DEFER_TASKRUN`.

Risks and test signals: unsupported kernels return skip on `-EINVAL`. Failures are missing custom flags, wrong CQE length/user data, bad sender completion, or remote thread failure.
