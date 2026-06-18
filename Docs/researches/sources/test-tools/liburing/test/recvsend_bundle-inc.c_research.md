# sources/test-tools/liburing/test/recvsend_bundle-inc.c

Purpose: tests send and receive bundle behavior with incremental receive buffer rings over TCP. It verifies sequence ordering while using a single large incremental receive buffer and optionally send bundles, receive bundles, or both.

Important APIs and types: `io_uring_prep_send_bundle`, `io_uring_prep_send`, `io_uring_prep_recv_multishot`, `IORING_RECVSEND_BUNDLE`, `IOU_PBUF_RING_INC`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUF_MORE`, `IORING_CQE_F_MORE`, pthread barriers, and TCP loopback sockets. This file includes `<liburing.h>` directly and defines local `T_EXIT_*` values.

Control flow: the receiver thread creates a CQ-sized ring, registers one huge incremental buffer covering `RECV_BIDS * MSG_SIZE`, accepts a TCP connection, arms multishot recv, and validates received sequence numbers. The sender creates a send buffer ring with `nr_msgs` 128-byte messages containing monotonic `unsigned long` sequences, optionally fills the socket toward `EAGAIN`, then sends either with `io_uring_prep_send_bundle()` or individual selected-buffer sends. `run_tests()` starts with four messages and covers no bundle, recv bundle, both bundles, full socket, almost full socket, and send-only bundle. It then repeats selected almost-full cases with 32 messages.

State and persistence: `recv_data.seq` is the expected sequence counter. `recv_bytes` is increased by backlog sends and bundle sends. `verify_sz` accumulates partial pieces until it has whole 128-byte messages to validate. The incremental receive ring must keep returning bid 0 with `IORING_CQE_F_BUF_MORE`.

Dependencies and integration: requires `IORING_FEAT_RECVSEND_BUNDLE` and incremental buffer ring support, checked through setup and `has_pbuf_ring_inc()`. Unsupported send bundle sets `no_send_mshot` and skips.

Risks and test signals: missing `BUF_MORE`, bid other than 0, sequence mismatch, bad send CQEs, or incomplete byte accounting fail. Passing demonstrates bundle sends and bundled multishot receives interoperate with incremental buffers under socket pressure.
