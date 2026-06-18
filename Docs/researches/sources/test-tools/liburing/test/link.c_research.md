# sources/test-tools/liburing/test/link.c

Purpose: validates basic linked SQE semantics, hard links, cancellation after a failing head, independent chains, and `submit_and_wait` behavior after early failure.

Important APIs/types/functions: `test_single_link`, `test_double_link`, `test_double_chain`, `test_single_link_fail`, `test_single_hardlink`, `test_double_hardlink`, `test_early_fail_and_wait`, `io_uring_prep_nop`, `io_uring_prep_timeout`, `io_uring_prep_remove_buffers`, `io_uring_prep_readv`, `IOSQE_IO_LINK`, and `IOSQE_IO_HARDLINK`.

Control flow: a normal ring and an IOPOLL ring are initialized. The suite submits NOP chains, a bad remove-buffer linked to a NOP, timeout hardlink chains, and an invalid readv chain with `io_uring_submit_and_wait`.

State and persistence behavior: ring-only state. `no_hardlink` records whether the kernel returns `-EINVAL` for hard links and skips later hardlink checks.

Dependencies and integration points: uses normal and `IORING_SETUP_IOPOLL` rings plus liburing/test helpers. It relies on exact CQE sequencing and link cancellation semantics.

Risks and test signals: expected results include successful NOP dependents, `-ENOENT` for invalid buffer removal, `-ECANCELED` for canceled dependents, `-ETIME` for hardlink timeouts, and no hang after early submit failure.
