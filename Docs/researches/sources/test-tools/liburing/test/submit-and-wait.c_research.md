# sources/test-tools/liburing/test/submit-and-wait.c

Purpose: verifies `io_uring_submit_and_wait_timeout()` returns promptly after timeout and does not wait twice when requested CQE count exceeds submitted work.

Important APIs/types/functions: `io_uring_submit_and_wait_timeout`, `io_uring_prep_nop`, `struct __kernel_timespec`, `mtime_since_now`, and `io_uring_queue_init_params`.

Control flow: queues one NOP, calls submit-and-wait-timeout asking for two CQEs with a one-second timeout, and verifies the call does not exceed roughly 1.2 seconds.

State/persistence behavior: only ring SQ/CQ state and a wall-clock measurement are used.

Dependencies/integration: tests liburing/kernel enter timeout semantics for partial completion.

Risks/test signals: catches double-wait behavior or unexpected negative return. It is timing-sensitive on very slow systems.
