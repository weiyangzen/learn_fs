# sources/test-tools/liburing/test/buf-ring-nommap.c

Purpose: tests mmap-provided buffer rings with an io_uring created using `IORING_SETUP_NO_MMAP` and caller-supplied memory. Key APIs are `io_uring_queue_init_mem`, `io_uring_register_buf_ring`, pbuf-ring `mmap`, `io_uring_buf_ring_add`, and selected-buffer pipe reads.

Control flow: allocate ring memory, initialize an unmapped ring, register/mmap one pbuf ring, add one buffer with bid 89, submit a selected-buffer read on a pipe, write data, and verify the CQE has `IORING_CQE_F_BUFFER` and the expected bid. State is transient ring memory and pbuf ring mapping. Risks are unsupported kernel features, mapping failures, or wrong buffer selection.
