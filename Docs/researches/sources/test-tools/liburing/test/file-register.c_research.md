<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/file-register.c -->
## sources/test-tools/liburing/test/file-register.c

Purpose: comprehensive fixed-file registration suite covering valid/invalid tables, updates, sparse sets, huge tables, allocation ranges, SCM-accounted fds, partial failure cleanup, and defer-taskrun interactions.

Important APIs/types/functions: `open_files`, `close_files`, `test_basic`, `test_sparse`, `test_additions`, `test_removals`, `test_grow`, `test_shrink`, `test_huge`, `test_skip`, `test_sparse_updates`, `test_fixed_removal_ordering`, `test_mixed_af_unix`, `test_partial_register_fail`, `test_file_alloc_ranges`, `io_uring_register_files`, `io_uring_register_files_update`, `io_uring_register_files_sparse`, `io_uring_register_file_alloc_range`, and `io_uring_prep_files_update`.

Control flow: `main` creates one base ring and runs ordered registration scenarios: normal registration, expected invalid fd failure, large table registration, sparse-table support probing, add/remove/replace/grow/shrink updates, zero-initialized sparse table fill, huge sparse table IO verification, skip marker behavior, full sparse update loops, fixed-file removal while linked IO is pending, mixed pipe/AF_UNIX registration, partial-register failure cleanup, allocation-range bounds, and optional defer-taskrun read/unregister behavior.

State and persistence behavior: many `.reg.*` and `.add.*` files are created and unlinked. Fixed-file tables hold references after original fds are closed. `no_update` gates update-dependent tests when sparse registration is unsupported.

Dependencies and integration points: central integration test for liburing fixed files, direct IO via fixed indexes, file allocator ranges, resource limits, sockets, pipes, and ring cleanup.

Risks: broad coverage means early failures can leave temporary files or descriptors. Some scenarios depend on `RLIMIT_NOFILE`, sparse-file-table kernel support, and SCM accounting behavior.

Test signals: pass is strong evidence that fixed-file table registration and update semantics are correct across normal and edge-case lifetimes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/file-register.c -->
