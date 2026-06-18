<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd-ring.c -->
## sources/test-tools/liburing/test/eventfd-ring.c

Purpose: checks that two rings can register different eventfds and poll each other's completion notifications without recursive or cross-ring confusion.

Important APIs/types/functions: `test(flags)`, `io_uring_queue_init_params`, `io_uring_queue_init`, `io_uring_register_eventfd`, `io_uring_prep_poll_add`, `io_uring_prep_nop`, and feature flag `IORING_FEAT_CUR_PERSONALITY`.

Control flow: `test` creates two rings, registers separate eventfds, queues a poll in each ring against the other ring's eventfd, submits both polls, then submits a NOP on the first ring to generate a completion signal. `main` runs the scenario once normally and once with `IORING_SETUP_DEFER_TASKRUN | IORING_SETUP_SINGLE_ISSUER`.

State and persistence behavior: each ring owns its own registered eventfd and pending poll SQE. The test intentionally does not reap CQEs or unregister eventfds, relying on process teardown.

Dependencies and integration points: exercises completion eventfd signaling, poll readiness, and defer-taskrun/single-issuer behavior.

Risks: because the test exits immediately after the triggering NOP submit, it mainly catches setup-time and obvious notification bugs, not detailed CQE ordering. Unsupported ring flags are treated as skip.

Test signals: pass indicates independent eventfd registration across rings and successful submissions in both normal and defer-taskrun modes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd-ring.c -->
