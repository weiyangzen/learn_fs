# sources/test-tools/liburing/test/nop32-overflow.c

Purpose: validates mixed 16-byte/32-byte CQE handling when a small CQ overflows.

Important APIs/types/functions: `IORING_SETUP_CQE_MIXED`, `IORING_SETUP_CQSIZE`, `IORING_NOP_CQE32`, `IORING_CQE_F_32`, `IORING_CQE_F_SKIP`, `io_uring_for_each_cqe`, `io_uring_cqe_nr`, and `io_uring_cq_advance`.

Control flow: creates an eight-entry SQ with a CQ size of eight but mixed CQE sizing. Submits eight NOPs where the first is normal and the rest request CQE32. It inspects visible CQEs for one normal, three 32-byte, and a skip CQE, advances by the correct CQE slot count, then waits for four overflowed 32-byte CQEs.

State and persistence behavior: transient CQ overflow state and sequence counter only.

Dependencies and integration points: depends on mixed CQE support and liburing helpers for iterating variable-sized CQEs.

Risks and test signals: detects incorrect CQE slot accounting, missing 32-bit flags, absent skip CQE, bad overflow flushing, or wrong user_data order after overflow.
