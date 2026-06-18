# sources/test-tools/liburing/test/resize-mmap-fail.c

Purpose: verifies ring resize failure handling when the new mmap cannot be created. The expected behavior is that `io_uring_resize_rings()` fails and the original ring remains valid and usable.

Important APIs and types: `io_uring_queue_init`, `io_uring_resize_rings`, `io_uring_prep_nop`, `io_uring_submit_and_wait`, `io_uring_peek_cqe`, `getrlimit`, `setrlimit`, `RLIMIT_AS`, `/proc/self/statm`, and `sysconf(_SC_PAGESIZE)`.

Control flow: `main()` initializes a small eight-entry ring and proves it works by submitting and completing a NOP. It reads current virtual memory size in pages, saves `RLIMIT_AS`, then sets a tight address-space limit to current usage plus two pages. It requests a resize to 64 SQ entries and 128 CQ entries, expecting failure due to mmap memory pressure. It restores the old limit immediately, requires a negative resize result, then submits and completes another NOP on the original ring.

State and persistence: the old ring mapping and ring bookkeeping must persist unchanged after failed resize. The process address-space limit is temporarily mutated and then restored before further checks.

Dependencies and integration: depends on `/proc/self/statm`, resource limits, and ring resize support. Inability to inspect VM size or page size skips; setup and resource-limit failures fail.

Risks and test signals: resize unexpectedly succeeding under the forced limit, inability to get an SQE after failure, submit failure, or missing completion after failure all indicate rollback bugs. Passing proves failed resize does not leave the ring broken.
