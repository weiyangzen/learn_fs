# sources/test-tools/liburing/test/read-inc-file.c

Purpose: tests regular-file reads with incremental provided buffer consumption. It specifically guards against a bug where the beginning of the incremental buffer was skipped when reading a normal file.

Important APIs and types: `io_uring_queue_init_params`, `io_uring_setup_buf_ring` with `IOU_PBUF_RING_INC`, `io_uring_buf_ring_add`, `io_uring_prep_read`, `IOSQE_BUFFER_SELECT`, and `IORING_CQE_BUFFER_SHIFT`. `BUF_BGID` and `BUF_BID` identify the single large provided buffer.

Control flow: `create_test_file()` writes eight 80-byte blocks containing repeated letters `a` through `h`. `arm_read()` submits an 80-byte selected-buffer read at a requested file offset. `main()` creates and opens the temporary file, sets up a 32-entry incremental buffer ring but publishes one 64 KiB buffer with bid 8, then issues four reads at offsets 0, 80, 160, and 240. Each completion must have a buffer flag, bid 8, result length 80, and the expected repeated character at the current buffer pointer; the local pointer then advances by `cqe->res`.

State and persistence: the kernel's incremental cursor into the single 64 KiB buffer persists across read operations. The test's `ptr` mirrors the expected cursor and checks that data is laid out sequentially from the start.

Dependencies and integration: requires incremental buffer ring support; `-EINVAL` from setup is treated as skip. Uses a temporary file named by pid and helper exit codes.

Risks and test signals: wrong bid, missing buffer flag, short read, or failure to find the expected character at the current cursor fails. Passing indicates regular-file reads consume incremental buffers from the correct initial offset.
