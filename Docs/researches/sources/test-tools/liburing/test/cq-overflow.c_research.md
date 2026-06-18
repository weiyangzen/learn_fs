# sources/test-tools/liburing/test/cq-overflow.c

Purpose: extensive CQ overflow and dropped-CQE coverage across NOPs, batch reaping, IOPOLL/defer modes, direct reads, and optional fault injection. Key APIs include `io_uring_cq_has_overflow`, `io_uring_get_events`, `io_uring_peek_batch_cqe`, `ring.cq.koverflow`, `IORING_FEAT_NODROP`, `IORING_SETUP_CQSIZE`, and direct `readv`.

Control flow: run overflow-handling combinations, validate fixed overflow counts, create `.cq-overflow`, submit many direct reads with increasing delays, and run a faulted-buffer case. State includes temporary file, iovec buffers, CQ overflow/dropped counters, and fairness counts. Risks are timing sensitivity, fault-injection differences, lost CQEs, bad ordering, or wrong overflow accounting.
