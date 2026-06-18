# sources/test-tools/liburing/test/sendmsg_iov_clean.c

Purpose: regression for non-immediate `sendmsg` completion when the submitted `msghdr`/iovec memory is stack-backed and could be reused after submission.

Important APIs/types/functions: `io_uring_prep_multishot_accept`, `io_uring_prep_sendmsg`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, pthread barrier synchronization, TCP sockets, `SO_SNDBUF`, and `SIGUSR1` notification.

Control flow: `main()` starts a TCP listener on port 9999 and queues multishot accept. A client thread connects, waits on a barrier, and drains incoming data. On accept CQE, `queue_sends()` shrinks the send buffer, fills it until `EAGAIN`, then queues 256 `sendmsg` SQEs using an iovec array in the caller-owned `msghdr`. The loop exits successfully after all send completions are observed.

State/persistence behavior: all state is sockets, in-flight sendmsg requests, stack iovecs, and the receiver thread. It intentionally pressures non-immediate completion paths by filling the socket send buffer.

Dependencies/integration: requires multishot accept and `SINGLE_ISSUER|DEFER_TASKRUN`; `-EINVAL` setup or accept support leads to skip. Uses a fixed localhost port, so parallel runs can conflict.

Risks/test signals: failure means lost send completions, use-after-return of iovec data, setup unsupported, or unexpected CQE user data. The test exits directly on success after seeing all sends.
