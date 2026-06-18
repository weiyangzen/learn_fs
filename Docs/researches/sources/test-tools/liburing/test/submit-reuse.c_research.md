# sources/test-tools/liburing/test/submit-reuse.c

Purpose: regression for submit-stable behavior where the kernel must not reuse caller iovec storage after submission, even when reads are punted to blocking context.

Important APIs/types/functions: `IORING_FEAT_SUBMIT_STABLE`, `io_uring_prep_readv`, `IOSQE_ASYNC`, `posix_fadvise(POSIX_FADV_DONTNEED)`, stack iovec arrays, background flusher thread, and `mtime_since_now`.

Control flow: `test_reuse()` initializes a ring and checks `SUBMIT_STABLE`, creates two files, starts a flusher thread that repeatedly evicts file pages, then for up to 1000 iterations or five seconds queues reads from both files. `prep()` constructs either one iovec or 16 split iovecs on the stack, submits, and immediately overwrites `iov_base` with NULL. `wait_nr()` requires nonnegative completions.

State/persistence behavior: creates temporary files `.reuse.1` and `.reuse.2` unless a path is supplied. The key state is the lifetime of submitted iovec memory versus kernel-side copied state.

Dependencies/integration: needs `IORING_FEAT_SUBMIT_STABLE` for meaningful coverage; otherwise it skips after first scenario. Uses filesystem cache eviction and pthreads to increase async/blocking likelihood.

Risks/test signals: a bad kernel may return `-EFAULT` or other negative CQEs after the iovecs are nulled. Timing and cache behavior affect how much async pressure is achieved.
