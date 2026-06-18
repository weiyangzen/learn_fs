# sources/test-tools/liburing/test/poll-many.c

Purpose: scales poll add/rearm over thousands of pipe fds to stress poll readiness and CQ handling.

Important APIs/types/functions: `NFILES=5000`, `BATCH=500`, `NLOOPS=1000`, `io_uring_prep_poll_add`, `IORING_SETUP_CQSIZE`, `RLIMIT_NOFILE`, `t_probe_defer_taskrun`, and pipe read/write.

Control flow: raises file descriptor limit when possible, creates many pipes, arms a poll on each, then for 1000 loops randomly triggers 500 untriggered pipes, reaps 500 CQEs, reads one byte, rearms each poll, and submits the rearm batch. It repeats under deferred-taskrun when supported.

State and persistence behavior: thousands of transient pipe fds and per-pipe `triggered` flags. No persistent files.

Dependencies and integration points: depends on high fd limits and optionally CQSIZE. Skips when not enough files can be opened and privileges cannot raise limits.

Risks and test signals: failures indicate lost poll readiness, rearm submit mismatch, bad CQ size behavior, or deferred-taskrun poll regressions.
