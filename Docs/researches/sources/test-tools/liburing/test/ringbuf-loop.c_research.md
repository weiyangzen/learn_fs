# sources/test-tools/liburing/test/ringbuf-loop.c

Purpose: regression test for incremental provided buffer rings where the receive buffer address is the buffer ring itself, ensuring buffer completion accounting survives the command overwriting ring entries.

Important APIs/types/functions: `io_uring_queue_init` with `IORING_SETUP_NO_SQARRAY`, `io_uring_setup_buf_ring`, `IOU_PBUF_RING_INC`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, `io_uring_prep_recv`, `IOSQE_BUFFER_SELECT`, and `io_uring_free_buf_ring`.

Control flow: the program creates a tiny provided buffer ring, adds the ring memory as a provided buffer, sends zero bytes over a UNIX datagram socketpair, and queues a receive selecting that buffer group. It waits for one completion, then frees the buffer ring and exits.

State/persistence behavior: ring memory is intentionally used as mutable data payload. The key state is the kernel-selected buffer metadata that must be committed even after the recv overwrites address/length fields in userspace memory.

Dependencies/integration: depends on provided buffer ring support, incremental buffer ring registration, UNIX datagram sockets, and `IORING_SETUP_NO_SQARRAY`. `-EINVAL` paths are treated as skips.

Risks/test signals: most regressions appear as kernel memory misuse, failed setup, failed completion, or teardown trouble rather than explicit payload checks.
