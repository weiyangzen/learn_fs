<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/evloop.c -->
## sources/test-tools/liburing/test/evloop.c

Purpose: guards against recursive completion generation when a ring polls its own registered completion eventfd with multishot poll.

Important APIs/types/functions: `io_uring_register_eventfd`, `io_uring_prep_poll_multishot`, `io_uring_prep_nop`, `io_uring_wait_cqe`, `io_uring_peek_cqe`, and `IORING_CQE_F_MORE`-style multishot behavior.

Control flow: `main` creates a ring and eventfd, registers the eventfd for completions, submits a multishot poll on that same eventfd, then submits a NOP. It consumes two CQEs and asserts no third CQE is immediately available.

State and persistence behavior: the ring's completion eventfd can trigger the ring's own poll request. The expected stable state is no runaway loop of additional completion notifications.

Dependencies and integration points: exercises eventfd notification, multishot polling, and CQ overflow avoidance.

Risks: older kernels may only stop recursion at overflow while newer kernels abort earlier. The test is sensitive to unexpected extra CQE production.

Test signals: pass means self-polling a registered eventfd does not recursively create unbounded completion events.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/evloop.c -->
