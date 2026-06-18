<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/file-update.c -->
## sources/test-tools/liburing/test/file-update.c

Purpose: validates fixed-file table updates across multiple rings and via `IORING_OP_FILES_UPDATE`.

Important APIs/types/functions: `test_update_multiring`, `test_sqe_update`, `test_update_no_table`, `io_uring_register_files`, `io_uring_register_files_update`, `io_uring_prep_files_update`, and `t_create_ring`.

Control flow: `main` creates three rings, registers the same initial fds into all three, updates all tables to new fds with and without explicit unregister, then submits a files-update SQE replacing ten entries with `-1`. It also tests a malformed update offset against a small table and accepts known error results.

State and persistence behavior: temporary `.reg.*` and `.add.*` files back the fd arrays and are cleaned after each scenario. Multi-ring fixed-file tables independently hold references to the same fd values.

Dependencies and integration points: exercises synchronous register update and asynchronous SQE-based files-update paths.

Risks: shared fd arrays across rings make ownership/refcount behavior important. Unsupported `IORING_OP_FILES_UPDATE` returns skip.

Test signals: pass means multi-ring updates, table removal, and invalid update offsets behave predictably.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/file-update.c -->
