# sources/test-tools/liburing/test/sqe-mixed-bad-wrap.c

Purpose: verifies `IORING_SETUP_SQE_MIXED` rejects a 128-byte SQE placed at the final 64-byte slot before ring wrap and remains usable afterward.

Important APIs/types/functions: `IORING_SETUP_SQE_MIXED`, `io_uring_prep_nop`, `io_uring_prep_nop128`, `io_uring_get_sqe`, CQE result validation, and sequence `user_data`.

Control flow: initializes an 8-entry mixed-SQE ring, submits seven normal NOPs to position the SQ tail at the last slot, submits a NOP128 that should fail, then submits a normal NOP that should still succeed.

State/persistence behavior: state is SQ tail position and mixed SQE slot accounting. No external state.

Dependencies/integration: requires mixed SQE setup support; unsupported kernels skip.

Risks/test signals: catches acceptance of an out-of-bound 128-byte SQE at wrap, broken recovery after the rejected SQE, or CQE result/user data corruption.
