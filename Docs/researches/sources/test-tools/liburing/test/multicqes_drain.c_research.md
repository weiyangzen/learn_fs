# sources/test-tools/liburing/test/multicqes_drain.c

Purpose: randomized and simple tests for drain ordering when multishot poll can produce multiple CQEs before cancellation.

Important APIs/types/functions: `io_uring_prep_poll_add`, `io_uring_prep_poll_multishot`, `io_uring_prep_poll_remove`, `io_uring_prep_nop`, `io_uring_get_events`, `io_uring_submit_and_get_events`, `IOSQE_IO_DRAIN`, `IOSQE_IO_LINK`, and `IORING_POLL_ADD_MULTI`.

Control flow: the simple test arms multishot and single poll, triggers events, then removes the multishot and submits a drained NOP, expecting the drained NOP last. The generic test randomly generates up to 50 operations across multishot poll, single poll, NOP, and cancel while avoiding illegal link/drain combinations, then verifies drained CQEs appear only after all prior non-multishot or canceled multishot work is complete.

State and persistence behavior: transient pipes and arrays tracking generated SQE metadata, active multishot requests, and completion bitmaps. No persistent files.

Dependencies and integration points: uses time-based randomness, pipes, optional deferred-taskrun mode, and liburing CQ event pumping helpers.

Risks and test signals: catches drain completion before earlier work, improper multishot cancellation accounting, lost events under deferred taskrun, or illegal ordering after randomized chains.
