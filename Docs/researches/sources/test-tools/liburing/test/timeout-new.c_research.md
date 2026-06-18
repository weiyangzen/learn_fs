# sources/test-tools/liburing/test/timeout-new.c

Purpose: focused tests for `io_uring_wait_cqe_timeout()` and multi-threaded getevents timeout behavior. It verifies returns both before and after timeout and checks that multiple waiters on the same ring handle wakeups without invalid errors.

Important APIs/types/functions: `msec_to_ts`, `test_return_before_timeout`, `test_return_after_timeout`, `__reap_thread_fn`, `reap_thread_fn0`, `reap_thread_fn1`, `test_multi_threads_timeout`, `io_uring_wait_cqe_timeout`, `io_uring_queue_init`, `io_uring_prep_nop`, and `IORING_SETUP_SQPOLL`.

Control flow: main initializes a normal ring, requires `IORING_FEAT_EXT_ARG`, and runs a NOP that should complete before a 200 ms timeout, then an empty wait that should return `-ETIME` near 200 ms. It repeats the same checks on an SQPOLL ring, with a one-shot retry for possible SQPOLL wakeup timing. Finally it starts two waiter threads, waits until both entered `io_uring_wait_cqe_timeout()`, submits one NOP, and accepts either one waiter consuming it or timeout on the other.

State/persistence behavior: only in-memory counters and thread return globals persist during the test. No files are created.

Dependencies/integration: exercises liburing's extended wait API, kernel `GETEVENTS` timeout support, SQPOLL submission, pthread synchronization, and helper timing `mtime_since_now`.

Risks/test signals: timing-sensitive around SQPOLL startup and thread scheduling. Failures are wrong timeout error, elapsed time outside 100-300 ms, bad NOP completion, or waiter return values other than success/`-ETIME`.
