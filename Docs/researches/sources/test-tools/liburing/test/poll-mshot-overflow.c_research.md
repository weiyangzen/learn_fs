# sources/test-tools/liburing/test/poll-mshot-overflow.c

Purpose: validates multishot poll behavior when CQ overflow occurs, including downgrade/no-more signaling and remove behavior.

Important APIs/types/functions: `io_uring_prep_poll_multishot`, `io_uring_prep_poll_remove`, `IORING_SETUP_CQSIZE`, `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, `IORING_CQE_F_MORE`, `io_uring_get_events`, and `io_uring_cq_ready`.

Control flow: `test_downgrade()` uses a two-entry CQ and repeatedly triggers a multishot poll to inspect whether overflow causes a final CQE without `MORE`. `test()` fills a tiny CQ with NOPs, triggers multishot poll overflow, drains NOPs, forces event processing, removes the poll, and validates final CQEs.

State and persistence behavior: transient pipe and CQ overflow state. No files.

Dependencies and integration points: uses `SINGLE_ISSUER` as a proxy for newer behavior and optionally deferred taskrun support.

Risks and test signals: failures are no downgrade on kernels expected to downgrade, `MORE` flag after terminal CQE, missing poll CQE, or unexpected user data while flushing overflow/removal.
