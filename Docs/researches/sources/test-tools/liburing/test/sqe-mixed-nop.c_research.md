# sources/test-tools/liburing/test/sqe-mixed-nop.c

Purpose: validates mixed 64-byte and 128-byte NOP SQEs, including SQ readiness/space accounting across wrap and `IORING_SETUP_SQ_REWIND`.

Important APIs/types/functions: `IORING_SETUP_SQE_MIXED`, `IORING_SETUP_SQ_REWIND`, `io_uring_get_sqe`, `io_uring_get_sqe128`, `io_uring_prep_nop128`, `io_uring_sq_ready`, `io_uring_sq_space_left`, and CQE user data sequencing.

Control flow: `test_flags()` alternates normal and 128-byte NOPs for 32 iterations, then `test_sq_space()` builds specific SQ occupancy sequences, checking that NOP128 consumes two or three slots depending on wrap behavior and rewind mode. It runs once without rewind and once with rewind.

State/persistence behavior: all state is mixed SQ tail/head accounting and CQ completions. No external resources.

Dependencies/integration: requires mixed SQE support and optionally SQ rewind support; unsupported setup skips.

Risks/test signals: catches wrong slot consumption, wrong ready/space counts, wrap handling bugs, CQE errors, and user_data sequencing errors.
