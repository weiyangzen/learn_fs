# sources/test-tools/liburing/test/nop-all-sizes.c

Purpose: exercises NOP submission and completion across ring depths from 1 up to 32768.

Important APIs/types/functions: `fill_nops`, `test_nops`, `io_uring_get_sqe`, `io_uring_prep_nop`, `io_uring_submit`, `io_uring_wait_cqe`, and `io_uring_queue_init`.

Control flow: for each power-of-two depth, creates a ring, fills and submits all available SQEs twice, then waits for the total number of completions before doubling depth. `-ENOMEM` stops the size sweep gracefully.

State and persistence behavior: ring allocation and CQ/SQ occupancy only. No filesystem state.

Dependencies and integration points: depends on memory limits and maximum allowed ring size. No helper status constants are used in the normal path.

Risks and test signals: catches off-by-one SQ fill behavior, submission count mismatch, CQ drain failures, and large-ring allocation or completion issues.
