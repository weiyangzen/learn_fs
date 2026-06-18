<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd.c -->
## sources/test-tools/liburing/test/eventfd.c

Purpose: validates eventfd-triggered completions and linked poll/read behavior on a ring with a registered eventfd.

Important APIs/types/functions: `io_uring_register_eventfd`, `io_uring_prep_poll_add`, `io_uring_prep_readv`, `io_uring_prep_nop`, `IOSQE_IO_LINK`, `POLLIN`, and `IORING_FEAT_CUR_PERSONALITY`.

Control flow: the test creates a ring, registers an eventfd, links a poll on the eventfd to a read of the same eventfd, then submits a NOP to trigger eventfd notification. It waits for three completions and validates the poll result, the eventfd read size, and the NOP success.

State and persistence behavior: eventfd counter state is consumed by the linked read. CQEs are acknowledged as they arrive; descriptor cleanup is left mostly to process exit.

Dependencies and integration points: integrates eventfd notification with poll, readv, linked SQEs, and completion delivery.

Risks: ordering can vary, so validation is keyed by `user_data`. Kernels without current-personality feature support skip the test.

Test signals: pass means eventfd notification wakes poll, the linked read consumes exactly one eventfd value, and unrelated NOP completion still appears.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd.c -->
