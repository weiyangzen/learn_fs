# sources/test-tools/liburing/test/socket-rw-eagain.c

Purpose: checks that a nonblocking socket `readv` queued before a `writev` returns `-EAGAIN` instead of waiting for later data on kernels without fast poll.

Important APIs/types/functions: TCP loopback sockets, `t_set_nonblock`, `io_uring_queue_init_params`, `IORING_FEAT_FAST_POLL`, `io_uring_prep_readv`, `io_uring_prep_writev`, and CQ iteration.

Control flow: creates a TCP connection, sets the receive side nonblocking, initializes a ring, skips if fast poll is present, queues readv on empty socket then writev on the peer, submits both, and expects CQEs for write length 128 and read `-EAGAIN`.

State/persistence behavior: state is socket readiness and CQ ordering. No files persist.

Dependencies/integration: specifically targets non-fast-poll behavior; fast-poll kernels skip because the semantics differ.

Risks/test signals: failure indicates blocking/merge behavior where the read consumes later data, wrong write length, or missing CQEs.
