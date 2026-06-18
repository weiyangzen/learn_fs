# sources/test-tools/liburing/test/recv-mshot-drain.c

Purpose: stress-tests multishot recv when the provided buffer ring is intentionally exhausted and refilled while data is actively arriving. It verifies that `-ENOBUFS` and missing `IORING_CQE_F_MORE` can be handled by refilling and rearming without data loss.

Important APIs and types: `io_uring_setup_buf_ring`, `io_uring_prep_recv_multishot`, `IOSQE_BUFFER_SELECT`, `IORING_CQE_F_BUFFER`, `IORING_CQE_F_MORE`, `io_uring_wait_cqe_timeout`, TCP loopback sockets, and pthread barriers.

Control flow: the receiver creates a four-entry 128-byte buffer ring, starts a sender thread, accepts a TCP connection, submits one multishot recv, and loops on CQEs with a two-second timeout. The sender transmits 4096 chunks of 64 bytes, with brief pacing. On `-ENOBUFS`, the receiver refills all four buffers and rearms. On normal data, it counts bytes, returns the selected buffer to the ring, and if `MORE` is absent while bytes remain, rearms the multishot request. EOF or timeout ends the loop. Final `total_recv` must equal `NR_SENDS * SEND_SIZE`.

State and persistence: `total_recv` accumulates bytes across multiple multishot lifetimes. The same buffer backing memory is recycled after each CQE. `thread_data` carries listener port synchronization to the sender.

Dependencies and integration: requires buffer rings and multishot recv; `-EINVAL` or `-ENOENT` during buffer ring setup skips. Uses TCP loopback and pthreads.

Risks and test signals: data loss, failure to rearm after exhaustion, mishandled `-ENOBUFS`, or byte-count mismatch fail. Passing shows buffer starvation is recoverable and multishot recv can be drained/refilled under sustained traffic.
