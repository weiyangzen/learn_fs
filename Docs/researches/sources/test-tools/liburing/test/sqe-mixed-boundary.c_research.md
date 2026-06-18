# sources/test-tools/liburing/test/sqe-mixed-boundary.c

Purpose: tests physical SQE boundary validation for mixed SQEs when the `sq_array` remaps a logical NOP128 to the last physical SQE slot.

Important APIs/types/functions: `IORING_SETUP_SQE_MIXED`, `t_io_uring_init_sqarray`, `io_uring_get_sqe128`, `io_uring_prep_nop128`, direct `ring.sq.array` manipulation, and expected `-EINVAL`.

Control flow: `test_valid_position()` confirms a normal NOP plus valid NOP128 succeeds. `test_oob_boundary()` advances tail state, overrides `sq_array[1]` to the last physical slot, writes a NOP128 there, submits, and requires the NOP128 CQE to fail with `-EINVAL` rather than reading past the SQE array.

State/persistence behavior: mutates userspace SQ array mapping directly to force the boundary condition. No external state.

Dependencies/integration: depends on helper support for initializing a ring with exposed sq_array and on mixed SQE kernel validation.

Risks/test signals: detects the historical 64-byte out-of-bounds read risk, missing CQE for the rejected SQE, or failure of a valid NOP128 placement.
