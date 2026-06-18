<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/futex.c -->
## sources/test-tools/liburing/test/futex.c

Purpose: comprehensive futex wait, wake, waitv, cancellation, ordering, and invalid-flag coverage for io_uring futex opcodes.

Important APIs/types/functions: `fwake`, `__test`, `test`, `test_order`, `test_multi_wake`, `test_wake_zero`, `test_invalid`, `io_uring_prep_futex_wait`, `io_uring_prep_futex_waitv`, `io_uring_prep_futex_wake`, `io_uring_prep_cancel64`, and `io_uring_register_sync_cancel`.

Control flow: the main matrix loops 500 times through scalar and vectored futex waits, spawning wake threads and racing async/non-async cancel requests. It then checks wake-zero semantics, invalid flag errors, SQPOLL and cooperative taskrun modes, wake ordering with one remaining wait canceled synchronously, and multi-wake completion of two waits.

State and persistence behavior: dynamically allocated futex words and `futex_waitv` arrays represent wait state. Global `no_futex` records unsupported kernels.

Dependencies and integration points: integrates futex2 flags, pthread wake helpers, io_uring async cancel, SQPOLL, COOP_TASKRUN, and sync cancel registration.

Risks: race-heavy; expected completion order is constrained only in specific ordering tests. Unsupported futex opcodes return `-EINVAL` or `-EOPNOTSUPP` and skip.

Test signals: pass strongly indicates futex wait/wake/cancel semantics are correct across ring modes.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/futex.c -->
