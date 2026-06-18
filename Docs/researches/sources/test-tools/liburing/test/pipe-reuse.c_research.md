# sources/test-tools/liburing/test/pipe-reuse.c

Purpose: checks that split pipe `readv` uses stable submitted iovecs even if userspace mutates them after submission.

Important APIs/types/functions: `io_uring_prep_readv`, `IORING_FEAT_SUBMIT_STABLE`, `struct iovec`, pipe writes, and `memcmp`.

Control flow: fills a 16-entry iovec over a 16 KiB buffer, writes half the data, submits readv, overwrites all iovec bases/lengths with invalid values, writes the second half, then waits and compares the received buffer to the original pattern.

State and persistence behavior: transient pipe and stack buffers only.

Dependencies and integration points: depends on `IORING_FEAT_SUBMIT_STABLE`; skips if absent. Uses pipe buffering to force split completion after userspace iovec mutation.

Risks and test signals: data mismatch or read error means the kernel reused mutated userspace iovec data rather than the stable submission copy. Short reads are ignored rather than fatal.
