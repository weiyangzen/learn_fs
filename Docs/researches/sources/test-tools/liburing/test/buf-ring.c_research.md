# sources/test-tools/liburing/test/buf-ring.c

Purpose: broad sanity coverage for provided buffer rings: lifecycle, invalid registration, classic-buffer conflicts, protected-page registration, normal selected reads, and mmap pbuf rings. Important APIs include `io_uring_setup_buf_ring`, `io_uring_register_buf_ring`, `io_uring_unregister_buf_ring`, `io_uring_prep_provide_buffers`, `IOU_PBUF_RING_MMAP`, and selected-buffer `read`.

Control flow: run registration and conflict tests over bgids 1 and 127, then read from `/dev/zero` using entry counts 1, 32768, and 4096 in normal and mmap modes, checking unique bids and final `-ENOBUFS`. State is transient buffer-ring registration and a bool array of consumed ids. Risks include unsupported kernels, buffer reuse, invalid registration acceptance, and wrong empty-ring behavior.
