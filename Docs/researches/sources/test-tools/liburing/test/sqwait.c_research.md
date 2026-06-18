# sources/test-tools/liburing/test/sqwait.c

Purpose: verifies `io_uring_sqring_wait()` lets applications obtain a new SQE after an SQPOLL ring becomes full under sustained I/O.

Important APIs/types/functions: `IORING_SETUP_SQPOLL`, `io_uring_sqring_wait`, `io_uring_get_sqe`, `io_uring_prep_read`, direct `O_DIRECT` reads, aligned iovecs, and bounded completion reaping.

Control flow: creates or uses a 256 MiB file, allocates 256 aligned buffers, initializes an 8-entry SQPOLL ring, opens the file with direct I/O, and loops 10,000 read submissions. When `get_sqe` returns NULL, it calls `io_uring_sqring_wait()` and immediately requires a new SQE to be available, while `reap()` keeps in-flight operations below half the buffer pool.

State/persistence behavior: temporary file is created/unlinked when no argv file is supplied. The primary state is SQ occupancy under SQPOLL and in-flight read count.

Dependencies/integration: needs SQPOLL, direct I/O support, and sufficient file size/access. `-EINVAL` from sqring wait or setup skips.

Risks/test signals: detects sqring wait not freeing SQEs, read CQE errors, direct I/O setup failures, and leaks/cleanup issues around many in-flight reads.
