# sources/test-tools/liburing/test/read-mshot.c

Purpose: comprehensive regression coverage for `IORING_OP_READ_MULTISHOT` on pipes with provided buffers. It covers normal and async submission, first-read-ready and not-ready cases, CQ overflow, invalid fd behavior, buffer length clamping, and incremental buffer consumption across several ring setup modes.

Important APIs and types: `io_uring_prep_read_multishot`, fallback single `io_uring_prep_read`, `io_uring_setup_buf_ring`, `IOU_PBUF_RING_INC`, `IOSQE_BUFFER_SELECT`, `IOSQE_ASYNC`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_SQPOLL`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, and CQE flags `IORING_CQE_F_BUFFER` and `IORING_CQE_F_MORE`.

Control flow: `test()` configures a pipe, ring, and buffer ring, optionally writes one message before arming, then submits a multishot read and writes enough messages to consume all buffers plus one. It verifies selected buffers, message size, optional incremental content, expected `-ENOBUFS`, and expected CQ overflow termination. `test_invalid()` submits multishot read on a temporary regular file and expects a final `-EBADFD` without `MORE`. `test_clamp()` registers buffers of 16 and 32 bytes, writes alternating sizes, and expects CQE lengths to match buffer capacity. `test_inc()` uses one large incremental buffer split into 2048-byte logical consumption, repeatedly writes 31-byte chunks, rearms when needed, and verifies each bid accumulates exactly 2048 bytes across normal, SQPOLL, and defer-taskrun modes.

State and persistence: global flags remember unsupported buffer rings, multishot read, and incremental rings. Incremental tests track current bid and bytes consumed per bid. The multishot request state persists until buffer exhaustion, overflow, invalid target, or lack of `MORE`.

Dependencies and integration: depends on pipes, temporary files, liburing buffer rings, and kernel support for multishot read. Unsupported features skip subsequent dependent cases rather than failing.

Risks and test signals: failures include missing `MORE`, missing buffer flag, wrong bid, truncated messages, unexpected overflow behavior, invalid-fd result other than `-EBADFD`, or incorrect clamping. Passing gives broad evidence that read multishot and provided buffer state machines behave across synchronous, async, overflow, and incremental paths.
