# sources/test-tools/liburing/test/pipe.c

Purpose: tests pipe creation through io_uring, both normal fd output and fixed-file direct output, with async requests, multiple ring modes, and too-small fixed tables.

Important APIs/types/functions: `io_uring_prep_pipe`, `io_uring_prep_pipe_direct`, `IORING_FILE_INDEX_ALLOC`, `io_uring_register_files_sparse`, `io_uring_prep_read`, `io_uring_prep_write`, `IOSQE_ASYNC`, `IOSQE_FIXED_FILE`, `IORING_SETUP_SQPOLL`, and `IORING_SETUP_DEFER_TASKRUN`.

Control flow: for normal, SQPOLL, and deferred rings, it runs eight parameter combinations of fixed/nonfixed, async/sync, and too-small table. Successful pipe creation is followed by a 32-byte write/read communication test. A fixed too-small table expects `-ENFILE`.

State and persistence behavior: transient pipe fds and fixed-file table slots. Normal fds are closed explicitly; ring exit releases fixed ones.

Dependencies and integration points: depends on pipe opcode and fixed pipe support. `-EINVAL` marks feature unsupported and skips.

Risks and test signals: failures include wrong pipe creation result, fixed table exhaustion not detected, bad communication through created fds, or mode-specific regressions under SQPOLL/deferred taskrun.
