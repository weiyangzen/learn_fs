# sources/test-tools/liburing/test/send_recvmsg.c

Purpose: tests UDP `sendmsg`/`recvmsg` through io_uring with single and multi-iovec receive buffers, legacy provided buffers, provided buffer rings, missing-buffer errors, and async mode.

Important APIs/types/functions: `io_uring_prep_recvmsg`, `io_uring_prep_sendmsg`, `io_uring_prep_provide_buffers`, `io_uring_setup_buf_ring`, `io_uring_buf_ring_add`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, buffer group `BUF_BGID`, and buffer id `BUF_BID`.

Control flow: `recv_fn()` creates a receive ring, optionally registers a buffer ring or provided buffer, queues `recvmsg`, then waits and validates the string payload or expected ENOBUFS. `do_sendmsg()` sends the fixed string to localhost UDP port 10203. `test()` synchronizes receiver and sender threads. `main()` runs sync and async cases across plain, multi-iov, buffer select, missing buffer, and buffer ring combinations.

State/persistence behavior: state is socket data, stack iovecs, optional provided-buffer registration, and global `ud` user data counter plus `no_pbuf_ring` feature cache.

Dependencies/integration: depends on pthreads, UDP localhost, provided buffer APIs, and kernel recvmsg support. Unsupported provide-buffers or buffer-ring paths are skipped by returning success from that scenario.

Risks/test signals: catches wrong payload length, string mismatch, wrong selected buffer id, missing ENOBUFS on no-buffer cases, and provided-buffer-ring support regressions.
