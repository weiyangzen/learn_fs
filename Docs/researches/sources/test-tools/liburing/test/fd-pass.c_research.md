<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fd-pass.c -->
## sources/test-tools/liburing/test/fd-pass.c

Purpose: verifies `MSG_RING` fixed-file passing between io_uring instances.

Important APIs/types/functions: `verify_fixed_read`, `test`, `io_uring_prep_msg_ring_fd`, `io_uring_prep_openat_direct`, `io_uring_prep_read`, `io_uring_prep_close_direct`, `IORING_FILE_INDEX_ALLOC`, `IOSQE_FIXED_FILE`, and `IORING_SETUP_DEFER_TASKRUN | IORING_SETUP_SINGLE_ISSUER`.

Control flow: `main` creates a patterned file, then runs source/target fixed-slot combinations in normal and defer-taskrun rings. Each scenario opens the file into a direct slot in the source ring, sends it to the destination ring, verifies the destination can read the pattern, closes the source slot, verifies source access fails, and confirms destination access still works.

State and persistence behavior: two rings own independent fixed-file tables. Passing duplicates the underlying file reference into the destination table; source close must not invalidate destination state.

Dependencies and integration points: exercises ring-to-ring messaging, fixed-file allocation, direct close, and data verification.

Risks: unsupported `MSG_RING` fd passing sets `no_fd_pass` and skips. Correctness hinges on reference ownership and slot allocation.

Test signals: pass proves fixed-file transfer preserves file contents and lifetime across rings.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fd-pass.c -->
