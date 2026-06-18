# sources/test-tools/liburing/test/recv-bundle-short-ooo.c

Purpose: tests multishot receive with bundle support and a small non-incremental buffer ring, verifying that data from a large TCP stream is received in byte order even when completions can cover multiple bundled buffers. It is based on a regression around receive bundle ordering.

Important APIs and types: `io_uring_register_buf_ring`, manually mapped `struct io_uring_buf_ring`, `io_uring_prep_recv_multishot`, `IORING_RECVSEND_BUNDLE`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_MORE`, socket-pair helper, and CQE buffer ID extraction. `struct buf_ring_data` tracks mapped ring memory and backing buffer memory.

Control flow: `setup_buf_ring()` mmap-allocates four 1024-byte buffers and a separate ring, registers bgid 0, fills the ring, and advances it. The test creates a connected stream socket pair, fills a 1 MiB pattern buffer, writes all bytes to the sender, closes sender, then submits four multishot receive SQEs with bundle and buffer selection. The completion loop processes CQEs until 1 MiB has been received or a poll-count cap is hit. `process_completion()` may split one CQE across several 1024-byte logical buffers, verifies each segment against the expected pointer, recycles buffers, and advances the expected cursor.

State and persistence: global `data_received` accumulates received bytes across completions. Buffer IDs and ring entries are recycled manually after each bundled segment. The expected-data pointer persists through the receive loop.

Dependencies and integration: runs under normal, defer-taskrun, SQPOLL, and cooperative task-run modes. Unsupported buffer ring or recv multishot support sets skip flags.

Risks and test signals: ordering mismatches, unexpected negative CQEs, incomplete 1 MiB transfer, or missing support handling fail. Passing demonstrates receive bundles preserve stream ordering while recycling a small buffer ring.
