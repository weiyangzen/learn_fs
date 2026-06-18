<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing.h -->
## sources/test-tools/liburing/src/include/liburing.h

Purpose: this is liburing's primary public API header. It exposes the user-space ring structures (`io_uring`, `io_uring_sq`, `io_uring_cq`, `io_uring_zcrx_rq`), queue setup/teardown entry points, submit/wait functions, registration wrappers, version APIs, and a large inline family of SQE preparation helpers.

Important APIs/types/functions: public initialization includes `io_uring_queue_init*`, `io_uring_queue_mmap`, `io_uring_ring_dontfork`, and `io_uring_queue_exit`. Completion APIs include `io_uring_wait_cqe*`, `io_uring_wait_cqes*`, `io_uring_peek_cqe`, `io_uring_peek_batch_cqe`, `io_uring_cqe_seen`, and `io_uring_cq_advance`. Submission helpers include `io_uring_get_sqe`, `io_uring_get_sqe128`, `io_uring_submit*`, and dozens of `io_uring_prep_*` functions for read/write, networking, poll, timeouts, file operations, xattrs, futex, uring command, pipe, fixed files, and zerocopy features. It also exposes buffer-ring helpers such as `io_uring_buf_ring_init`, `io_uring_buf_ring_add`, `io_uring_buf_ring_advance`, and `io_uring_buf_ring_available`.

Control flow: applications allocate or map a ring, fetch SQEs through `io_uring_get_sqe`, fill them with `io_uring_prep_*`, submit with `io_uring_submit*`, consume CQEs with peek/wait helpers, and release CQ head with `io_uring_cqe_seen` or `io_uring_cq_advance`. Inline CQ iteration uses acquire reads of kernel tail and release stores of user head. Mixed/big SQE and CQE modes are handled by shift helpers and skip-CQE logic.

State and persistence behavior: the header defines in-memory shared-ring state only. Persistent state is file-descriptor based through `ring_fd`/`enter_ring_fd` and registered resources owned by the kernel. User data is carried in `sqe->user_data` and returned in CQEs. SQ/CQ indices, ring masks, flags, and entry counts are shared with the kernel and must be updated with the barrier helpers.

Dependencies and integration points: includes the UAPI `io_uring.h`, query and BPF filter headers, compatibility headers, socket/stat/uio/time/fcntl/signal system headers, and `barrier.h`. The declarations are implemented across `setup.c`, `queue.c`, `register.c`, `syscall.c`, `sanitize.c`, and `version.c`. C++20 module compatibility is addressed through `IOURINGINLINE` and `_LOCAL_INLINE`.

Risks: this header is ABI-sensitive. Incorrect field initialization in prep helpers can corrupt kernel requests, and wrong memory ordering around SQ/CQ head/tail can race the kernel. Direct descriptors encode indexes as `index + 1`, with special handling for `IORING_FILE_INDEX_ALLOC`; mistakes there can close or allocate the wrong fixed slot. The inline receive-message accessors guard against integer overflow, but callers must still pass matching buffers and `msghdr` sizes.

Test signals: the listed tests exercise read/write over sockets, accept variants, fixed files, multishot accept, SQ array compatibility, cross-fork mapping behavior, and syzkaller regressions. This header's prep helpers and queue helpers are directly used by almost every test file.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/src/include/liburing.h -->
