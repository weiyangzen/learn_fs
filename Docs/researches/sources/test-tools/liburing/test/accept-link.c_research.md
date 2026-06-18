<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/accept-link.c -->
## sources/test-tools/liburing/test/accept-link.c

Purpose: tests linked accept and timeout behavior, including cases where a client connects before or after timeout and where linked requests should complete with expected result combinations.

Important APIs/types/functions: thread coordination helpers `signal_var` and `wait_for_var`; `struct data` records expected CQE results, timeout, endpoint address, and stop flag. `send_thread` connects to the receiver. `recv_thread` prepares accept linked with timeout and validates completions. `test_accept_timeout` drives scenarios.

Control flow: for each scenario, receiver creates a listen socket, queues an accept SQE linked to a timeout SQE, starts or suppresses a client connection, submits, and validates two CQEs against expected result classes. Threads synchronize readiness and completion with condition variables.

State and persistence behavior: only per-test socket descriptors, thread flags, ring state, and port/address values are retained. They are cleaned at test end.

Dependencies and integration points: uses pthreads, TCP sockets, poll-related timing, `io_uring_prep_accept`, `io_uring_prep_link_timeout`, linked SQE flags, submit/wait, and helper networking functions.

Risks: timeout tests are inherently timing-sensitive. A slow system can produce borderline ordering failures if timeout and connect race differently than expected. Correct handling of linked timeout cancellation is the key behavioral risk.

Test signals: validates accept/link-timeout CQE ordering and result propagation.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/accept-link.c -->
