# File Research: sources/os/linux/linux/io_uring/io_uring.c

Core io_uring engine: owns ring context allocation, setup/enter syscalls, SQE submission, CQE posting, async fallback, io-wq integration, linked/drained request sequencing, iopoll handling, context teardown, and global initialization.

Key flows:
- Setup path: `io_uring_setup()` copies user params, `io_prepare_config()` validates flags/sizes/layout, `io_uring_create()` allocates `io_ring_ctx`, creates mmap regions, starts SQPOLL/offload if requested, publishes params, creates anon inode file, and installs or registers the ring fd.
- Enter path: `io_uring_enter()` resolves normal or registered ring fd, handles loop mode, SQPOLL wake/wait, direct submission via `io_submit_sqes()`, and completion waits through iopoll or `io_cqring_wait()`.
- Submission path: `io_submit_sqes()` consumes SQEs with stable `READ_ONCE()` loads, allocates cached `io_kiocb`s, validates opcode/flags/restrictions, handles SQE128/SQE_MIXED, credentials/personality, BPF filters, links, drains, and then issues inline or punts.
- Issue path: `io_issue_sqe()` assigns files, calls opcode `prep`/`issue` table functions, converts `IOU_COMPLETE` into deferred/post completions, and tracks iopoll requests.
- Async path: `io_queue_async()`, `io_queue_iowq()`, `io_wq_submit_work()`, and task-work helpers manage `-EAGAIN`, poll arming, io-wq retries, forced async, worker cancellation, and multishot restrictions.
- Completion path: CQE cache refill, CQ overflow storage, aux CQEs, mixed/32-byte CQEs, deferred completion batching, eventfd/poll/timeout flush, and overflow drop reporting.
- Teardown path: `io_ring_ctx_wait_and_kill()` kills refs and schedules exit work; `io_ring_exit_work()` cancels requests, reaps iopoll, detaches task contexts, synchronizes deferred task work, then `io_ring_ctx_free()` unregisters resources and frees mapped regions.

Important details:
- The opening comment documents user/kernel memory ordering for SQ/CQ head/tail.
- `io_uring_allowed()` enforces sysctls, group gating, CAP_SYS_ADMIN bypass, and LSM approval.
- `rings_size()` computes ring/SQE layout including `NO_SQARRAY`, `SQE128`, `CQE32`, and mixed modes.
- `io_cqring_add_overflow()` preserves completion ordering when CQ is full and tracks dropped CQEs.
- `io_drain_req()` and `io_queue_deferred()` serialize drains by comparing allocated and drained request counts.
- File assignment prevents fixed io_uring files and tracks inflight normal io_uring file refs for cancellation.
- Init validates UAPI structure offsets and creates the `io_kiocb` slab with hardened usercopy metadata.
