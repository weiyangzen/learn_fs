# sources/test-tools/liburing/test/recv-bundle-buf-len.c

Purpose: validates that non-incremental provided buffer descriptors are not persistently corrupted by receive bundle operations that trim the head buffer or fail before consuming data. It targets regressions where a bundle recv shrank `buf->len` and poisoned later operations.

Important APIs and types: `io_uring_prep_recv`, `IORING_RECVSEND_BUNDLE`, `IOSQE_BUFFER_SELECT`, `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `io_uring_buf_ring_mask`, `IORING_FEAT_RECVSEND_BUNDLE`, socketpair, pipe, and CQE buffer-id extraction.

Control flow: `setup()` initializes a ring, verifies bundle feature support, allocates two 4096-byte buffers, registers a non-incremental buffer ring, and publishes both entries. `test_eagain_no_corrupt()` submits a bundle recv with `MSG_DONTWAIT` and `len=1` on an empty datagram socket, expects `-EAGAIN`, verifies `t.br->bufs[0].len` is still 4096, then performs a selected-buffer pipe read that must consume all 4096 bytes using bid 0. `test_success_trim()` writes 64 bytes to a stream socket, submits a bundle recv with `SHORT_LEN` 32, expects `res == 32`, bid 0, and matching payload.

State and persistence: the raw buffer ring descriptor length is explicitly inspected after a failed recv. Buffer group state is reused by a later unrelated read in the first case to prove user-visible behavior is intact.

Dependencies and integration: requires kernel receive/send bundle feature and buffer rings; unsupported paths set `no_bundle` or `no_buf_ring` and skip. Uses helper exit codes.

Risks and test signals: corrupted descriptor length, wrong completion result, missing buffer flag, wrong bid, or data mismatch fail. Passing shows failed and successful bundle trims do not damage buffer-ring descriptor state beyond intended consumption.
