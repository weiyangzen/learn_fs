# sources/test-tools/liburing/test/poll.c

Purpose: exercises several poll corner cases: basic child-process pipe polling, multishot poll event aggregation under deferred task-run rings, polling an io_uring ring fd from another ring, and lazy poll activation for rings created disabled. It targets regressions where poll events are lost or poll wakeups get stuck.

Important APIs and types: `io_uring_prep_poll_add`, `io_uring_prep_poll_multishot`, `io_uring_enable_rings`, `io_uring_for_each_cqe`, `io_uring_peek_cqe`, `socketpair`, `setsockopt`, `fork`, and `pipe`. The setup flags `IORING_SETUP_SINGLE_ISSUER`, `IORING_SETUP_DEFER_TASKRUN`, and `IORING_SETUP_R_DISABLED` are central.

Control flow: `test_basic()` forks; the child polls the pipe read end and validates a `POLLIN` completion after the parent writes. `test_missing_events()` uses a socketpair with constrained send buffer, submits a multishot `POLLIN|POLLOUT`, triggers both directions, drains all CQEs, and verifies the aggregate mask contains both bits. `test_self_poll()` submits many polls against `ring.ring_fd`, then posts a NOP to ensure the self-polling path makes progress. `test_disabled_ring_lazy_polling()` checks both early and late polling of a disabled defer-taskrun ring: another ring polls its `ring_fd`, the target ring is enabled, a NOP is submitted, and exactly one CQE should appear.

State and persistence: per-test rings and sockets are independent. `res_mask` accumulates multishot results. Disabled ring state persists until `io_uring_enable_rings()` and is the behavior under test.

Dependencies and integration: feature-gated by `t_probe_defer_taskrun()` for deferred task-run cases. Uses helpers for exit codes and error handling.

Risks and test signals: failures expose lost poll events, missing `POLLOUT`, stuck poll wait queues, or incorrect ring-fd readiness. Passing signals include `POLLIN` from basic pipe, both `POLLIN|POLLOUT` observed in multishot, self-poll progress after NOP, and one CQE from the lazy polling scenarios.
