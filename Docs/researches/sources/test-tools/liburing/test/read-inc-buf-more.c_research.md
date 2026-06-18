# sources/test-tools/liburing/test/read-inc-buf-more.c

Purpose: verifies `IORING_CQE_F_BUF_MORE` is correctly set for incremental provided buffer rings (`IOU_PBUF_RING_INC`) on both pollable pipes and regular files, including EOF. It targets bugs where early buffer commit paths or zero-length EOF reads dropped the `BUF_MORE` signal even though the buffer still had remaining space.

Important APIs and types: `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, `io_uring_free_buf_ring`, `io_uring_prep_read`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, `IORING_CQE_F_BUF_MORE`, and `IOU_PBUF_RING_INC`. Constants define one 256-byte buffer and 32-byte read requests.

Control flow: `do_read()` submits a selected-buffer read, waits for one CQE, rejects negative results, requires `IORING_CQE_F_BUFFER`, and requires `IORING_CQE_F_BUF_MORE`. `test_pipe()` installs one incremental buffer, writes 12 bytes to a pipe, verifies a 12-byte read with `BUF_MORE`, closes the write end, and verifies EOF with `BUF_MORE`. `test_file()` creates a temporary file with four 32-byte chunks, reads four fixed-size chunks through the same single incremental buffer, and requires `BUF_MORE` each time.

State and persistence: `no_buf_ring_inc` records unsupported incremental buffer rings. The single buffer persists and is incrementally consumed across reads, which is the state under test. Temporary files are unlinked on normal and most error paths.

Dependencies and integration: depends on buffer ring registration and selected-buffer reads. `-EINVAL` from buffer ring setup is a skip signal.

Risks and test signals: missing `BUF_MORE`, missing buffer flag, wrong read lengths, or read errors fail. Passing demonstrates both locked and early commit paths preserve incremental buffer remaining-state metadata.
