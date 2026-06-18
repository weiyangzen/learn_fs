<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-reuse.c -->
## sources/test-tools/liburing/test/fixed-reuse.c

Purpose: verifies linked direct-open/read/close in a reused fixed-file slot sees the new file, not stale slot state.

Important APIs/types/functions: `io_uring_prep_openat_direct`, `io_uring_prep_read`, `io_uring_prep_close_direct`, `io_uring_register_files`, `IOSQE_FIXED_FILE`, `IOSQE_IO_LINK`, and feature `IORING_FEAT_CQE_SKIP`.

Control flow: the test creates two patterned files, registers an empty fixed-file table, opens the first file into slot 0, then submits a linked chain that opens the second file into slot 0, reads from fixed slot 0, and closes it. It validates completions and checks the buffer contains the second file's pattern.

State and persistence behavior: fixed slot 0 is deliberately reused. The core state is direct descriptor replacement across a linked operation chain.

Dependencies and integration points: integrates direct open/close, fixed-file reads, linked ordering, and fixed slot table setup.

Risks: skipped if `IORING_FEAT_CQE_SKIP` is absent. Pattern validation catches stale reference use.

Test signals: pass means fixed slot reuse is ordered correctly and reads observe the newly opened file.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fixed-reuse.c -->
