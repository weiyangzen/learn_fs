# sources/test-tools/liburing/test/madvise.c

Purpose: basic `IORING_OP_MADVISE` test that uses mmap copy timings as a soft signal for `MADV_DONTNEED` and `MADV_WILLNEED`.

Important APIs/types/functions: `do_madvise`, `test_madvise`, `io_uring_prep_madvise`, `io_uring_submit_and_wait`, `mmap`, `msync`, `MADV_DONTNEED`, `MADV_WILLNEED`, `t_create_file`, and `utime_since_now`.

Control flow: creates or uses a file, mmaps 128 KiB, copies it twice for cached timing, submits DONTNEED, copies again, submits DONTNEED then WILLNEED, syncs, and copies again. `main()` repeats up to 100 loops but exits early after at least ten good runs without bad timing.

State and persistence behavior: may create `.madvise.tmp` and unlinks it unless an input filename was supplied. Kernel page cache state is the behavior under test.

Dependencies and integration points: depends on mmap, filesystem page cache, io_uring madvise support, and helpers for temporary file creation.

Risks and test signals: `-EINVAL`/`-EBADF` skips unsupported kernels. Timing is intentionally treated as unreliable; hard failures are setup, CQE, mmap, or unexpected madvise errors.
