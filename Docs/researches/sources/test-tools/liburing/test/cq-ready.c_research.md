# sources/test-tools/liburing/test/cq-ready.c

Purpose: verifies `io_uring_cq_ready` count accuracy. Important APIs are `io_uring_cq_ready`, `io_uring_cq_advance`, and NOP submissions.

Control flow: check zero ready, submit four NOPs and expect four, advance all, submit four again, then advance by 1/2/1 while expecting 3/1/0 ready counts. State is CQ head/tail only. Risks are stale cached readiness or bad advance math.
