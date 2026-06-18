# sources/test-tools/liburing/test/nop32.c

Purpose: verifies `IORING_NOP_CQE32` produces 32-byte CQEs with expected extra fields on a mixed-CQE ring.

Important APIs/types/functions: `IORING_SETUP_CQE_MIXED`, `IORING_NOP_CQE32`, `IORING_CQE_F_32`, `sqe->off`, `sqe->addr`, and `cqe->big_cqe`.

Control flow: initializes a mixed-CQE ring, submits one ordinary NOP, then submits 16 CQE32 NOPs with increasing `off` and `addr` values and validates `big_cqe[0]` and `[1]` against expected counters.

State and persistence behavior: in-memory sequence and expected extra counters only.

Dependencies and integration points: depends on mixed CQE and NOP CQE32 support; `-EINVAL` setup skips.

Risks and test signals: catches missing `IORING_CQE_F_32`, corrupted extra fields, or broken ordinary NOP behavior on a mixed ring.
