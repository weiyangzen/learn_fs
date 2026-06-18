# sources/test-tools/liburing/test/cq-full.c

Purpose: simple CQ overflow/full-ring test using NOPs. Important APIs are `io_uring_queue_init_params`, `io_uring_prep_nop`, `io_uring_peek_cqe`, `io_uring_cqe_seen`, `ring.cq.koverflow`, and `IORING_FEAT_NODROP`.

Control flow: create a four-entry ring, submit three batches of four NOPs without draining, then drain visible CQEs and validate completion count plus overflow accounting. State is CQ head/tail and overflow counter. Risks are feature-dependent overflow semantics and incorrect CQ accounting.
