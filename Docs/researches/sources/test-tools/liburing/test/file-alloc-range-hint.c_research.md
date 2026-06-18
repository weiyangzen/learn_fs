<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/file-alloc-range-hint.c -->
## sources/test-tools/liburing/test/file-alloc-range-hint.c

Purpose: verifies auto-allocated fixed-file slots honor a configured allocation range even after operations outside the range update allocation hints.

Important APIs/types/functions: `file_update_alloc`, `test_hint_below_range`, `test_hint_above_range`, `io_uring_register_files_sparse`, `io_uring_register_file_alloc_range`, `io_uring_register_files_update`, and `IORING_FILE_INDEX_ALLOC`.

Control flow: the below-range scenario creates a sparse 20-slot table, limits auto-allocation to `[10,20)`, installs/removes a file at slot 2, then auto-allocates another fd and checks the returned slot remains inside range. The above-range scenario configures `[0,10)`, installs at slot 15, and checks auto-allocation still stays inside `[0,10)`.

State and persistence behavior: sparse fixed-file tables and kernel allocation hints are the core state. Pipe fds are closed and rings exited per scenario.

Dependencies and integration points: targets fixed-file sparse tables, allocation ranges, and userspace writeback of allocated slot indexes.

Risks: unsupported sparse registration skips. Failure indicates allocation hint corruption can escape configured bounds.

Test signals: pass means both below-range and above-range hint perturbations still allocate within the configured range.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/file-alloc-range-hint.c -->
