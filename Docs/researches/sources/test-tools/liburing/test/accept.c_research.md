<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept.c -->
## sources/test-tools/liburing/test/accept.c

Purpose: comprehensive accept regression suite covering normal accept, queued-before-connect accept, nonblocking listeners, fixed direct descriptors, multishot accept, overflow interactions, SQPOLL restrictions, cancellation, and pending accepts during ring exit.

Important APIs/types/functions: helper structs `data`, `accept_test_args`, and `test_accept_many_args`; helpers `queue_send`, `queue_recv`, `queue_accept_multishot`, `queue_accept_conn`, `accept_conn`, `start_accept_listen`, `set_client_fd`, `cause_overflow`, `clear_overflow`, `test_loop`, `test`, `test_accept_many`, `test_accept_cancel`, and scenario wrappers for normal/multishot/fixed/SQPOLL cases.

Control flow: main runs a sequence of scenarios, stopping on hard failure and skipping when feature detection shows accept or multishot accept unsupported. Each loop creates listen/client sockets, queues accepts before or after client connection, accepts CQEs while ignoring synthetic NOP overflow CQEs, optionally validates data transfer through accepted sockets, and checks direct/fixed file indexes. Cancellation tests queue accepts, then async cancels by user data and verify `-ECANCELED`, `-EINTR`, `-EALREADY`, or zero as appropriate.

State and persistence behavior: `no_accept` and `no_accept_multi` globally record unsupported features. Fixed file tables, overflow CQEs, socket arrays, and rings are per scenario and cleaned. `test_accept_many` temporarily lowers/restores `RLIMIT_NPROC`.

Dependencies and integration points: exercises `liburing.h` accept prep variants, fixed-file registration, multishot `IORING_CQE_F_MORE`, cancellation, SQPOLL setup, queue overflow handling, and read/write verification.

Risks: broad coverage means multiple kernel features influence outcomes. Overflow handling, multishot rearming, fixed-slot allocation, and cancellation timing are the most fragile behaviors. Resource-limit manipulation must restore state even on failures.

Test signals: this is the strongest signal for accept correctness across liburing's high-level helper surface and kernel feature matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept.c -->
