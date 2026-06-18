# sources/test-tools/liburing/test/waitid.c

Purpose: validates io_uring `waitid` support across successful child reaping, linked timeout cancellation, pid filtering, ready children, explicit cancellation, invalid `siginfo_t` pointers, and cancellation races.

Important APIs/types/functions: `child`, `test_invalid_infop`, `test_noexit`, `test_double`, `test_ready`, `test_cancel`, `test_cancel_race`, `test`, `io_uring_prep_waitid`, `io_uring_prep_link_timeout`, `io_uring_prep_cancel64`, `P_PID`, `P_ALL`, `WEXITED`, `IOSQE_IO_LINK`, and `IOSQE_ASYNC`.

Control flow: main initializes one ring and first runs a basic waitid test; `-EINVAL` marks unsupported and skips the rest. It then checks a wait linked to a 100 ms timeout against a child that exits after 200 ms, expecting waitid `-ECANCELED` and timeout result `1`. It verifies a wait for the second of two children ignores the first child, reaps an already-exited child, cancels a pending wait by user data, verifies invalid user `siginfo_t` returns `-EFAULT`, and runs 1000 cancellation races alternating async/non-async waitid.

State/persistence behavior: creates many child processes and reaps them with either io_uring waitid or fallback `wait`. No files are used.

Dependencies/integration: depends on process creation, wait queues, signal/child exit semantics, io_uring cancellation, link timeout support, and race tolerance around cancellation.

Risks/test signals: highly race-oriented. Expected race outcomes include wait completion or cancellation, and cancel CQEs may return `1`, `0`, `-ENOENT`, or `-EALREADY`. Other result codes, wrong `si_pid`, or unreaped children indicate failures.
