# sources/test-tools/liburing/test/recv-multishot.c

Purpose: comprehensive multishot recv and recvmsg validation across stream/datagram sockets, wait-each versus batched waits, deferred task-run, and early-error scenarios. It also validates liburing recvmsg output parsing helpers and explicit `-ENOBUFS` behavior.

Important APIs and types: `io_uring_prep_recv_multishot`, `io_uring_prep_recvmsg_multishot`, `io_uring_prep_provide_buffers`, `io_uring_prep_cancel64`, `io_uring_recvmsg_validate`, `io_uring_recvmsg_payload`, `io_uring_recvmsg_payload_length`, `io_uring_recvmsg_name`, `io_uring_recvmsg_cmsg_firsthdr`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_MORE`, `IORING_CQE_F_BUFFER`, and socket helpers.

Control flow: `test_recvmsg_validate()` first checks helper bounds handling. The main nested loop runs 16 combinations of stream/datagram, wait strategy, recv versus recvmsg, and defer mode, and for each combination runs early-error modes: none, not enough buffers, early sender close, early receiver cancel, and CQ overflow. `test()` provides buffers of alternating sizes, submits one multishot receive, sends progressively larger integer payloads, optionally triggers an early condition, collects CQEs, and validates final/non-final flags, selected buffer presence, payload order, recvmsg name/control metadata for datagrams, truncation accounting, and expected errors. `test_enobuf()` separately proves that two buffers followed by three datagrams produce two data CQEs and a final `-ENOBUFS` CQE without buffer or more flags.

State and persistence: arrays keep sent buffer pointers, allocated receive buffers, and copied CQEs for later validation. Totals track sent, received, and truncated bytes. `user_data` distinguishes provide-buffer, receive, and cancel operations.

Dependencies and integration: requires multishot receive support; initial unsupported behavior returns `T_EXIT_SKIP`. Defer mode is gated by `t_probe_defer_taskrun()`.

Risks and test signals: this is a high-value protocol-state test. Failures catch wrong final `MORE`, missing buffer flags, invalid recvmsg layout, address/control corruption, dropped bytes without truncation accounting, incorrect early errors, or malformed `-ENOBUFS`.
