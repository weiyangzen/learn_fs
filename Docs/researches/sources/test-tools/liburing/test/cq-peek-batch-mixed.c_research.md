# sources/test-tools/liburing/test/cq-peek-batch-mixed.c

Purpose: validates batch CQE peeking on `IORING_SETUP_CQE_MIXED` rings with 16-byte CQEs, 32-byte CQEs, and internal skip entries. Important APIs are `IORING_NOP_CQE32`, `IORING_CQE_F_32`, `IORING_CQE_F_SKIP`, `io_uring_cqe_nr`, and `io_uring_peek_batch_cqe`.

Control flow: submit mixed NOP completions, check logical batch counts and big CQE payloads, advance by physical slot count, then construct a wrap case where a skip entry must be consumed internally and not returned. State is CQ head/slot width math. Risks are exposed skip CQEs, wrong batch counts, or bad big-CQE data.
