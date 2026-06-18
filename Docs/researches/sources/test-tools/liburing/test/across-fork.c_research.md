<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/across-fork.c -->
## sources/test-tools/liburing/test/across-fork.c

Purpose: tests ring behavior across fork boundaries, including whether `io_uring_ring_dontfork` prevents unsafe inherited mappings and whether parent/child can perform expected writes.

Important APIs/types/functions: `struct forktestmem` stores shared test state. `open_tempfile`, `submit_write`, `wait_cqe`, `verify_file`, and `cleanup` manage file I/O and validation. `main` coordinates parent/child execution.

Control flow: creates a temporary directory/file, initializes a ring, optionally marks ring mappings `MADV_DONTFORK`, forks, submits writes from parent and/or child depending on the scenario, waits for CQEs, verifies file content, and cleans up.

State and persistence behavior: temporary files persist only for test duration. Ring mappings may or may not be inherited across fork depending on the tested call. Shared memory or process-local state coordinates expected content.

Dependencies and integration points: uses `io_uring_queue_init`, `io_uring_ring_dontfork`, write prep, submit/wait, fork/wait, file helpers, and cleanup syscalls.

Risks: forked processes using inherited shared mappings can fail in subtle ways if kernel/liburing expectations change. Cleanup must handle child failure paths and temporary directory removal.

Test signals: validates setup.c's `io_uring_ring_dontfork` and safe behavior around forked processes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/across-fork.c -->
