<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd-reg.c -->
## sources/test-tools/liburing/test/eventfd-reg.c

Purpose: verifies eventfd registration lifetime rules on a single io_uring instance.

Important APIs/types/functions: `io_uring_queue_init_params`, `eventfd`, `io_uring_register_eventfd`, `io_uring_unregister_eventfd`, and the `T_EXIT_*` test result constants.

Control flow: `main` creates one ring and two eventfds, registers the first eventfd, verifies that a second registration fails with `-EBUSY`, unregisters the first eventfd, then performs 100 register/unregister cycles to catch reference-counting and repeated-state bugs.

State and persistence behavior: the ring keeps at most one registered completion eventfd. The test creates kernel eventfd state and closes descriptors before exit, but it does not call `io_uring_queue_exit`.

Dependencies and integration points: depends on eventfd support, liburing registration helpers, and normal test skip behavior when invoked with extra arguments.

Risks: leaks are possible on early failure because cleanup is minimal. The important regression risk is accepting duplicate eventfd registrations or failing to fully clear ring eventfd state.

Test signals: pass means duplicate registration returns `-EBUSY` and repeated register/unregister remains stable.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/eventfd-reg.c -->
