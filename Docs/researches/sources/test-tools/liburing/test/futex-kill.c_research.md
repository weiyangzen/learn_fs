<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/futex-kill.c -->
## sources/test-tools/liburing/test/futex-kill.c

Purpose: ensures killing a process with an active private futex wait through io_uring does not leave bad state or crash.

Important APIs/types/functions: `do_child`, `test`, `io_uring_prep_futex_wait`, `io_uring_prep_futex_waitv`, `FUTEX2_PRIVATE`, `FUTEX2_SIZE_U32`, `IORING_SETUP_SQPOLL`, and `IOSQE_ASYNC`.

Control flow: each scenario forks a child that creates a ring, allocates a futex word, submits either scalar or vectored private futex wait, optionally async and optionally SQPOLL, then exits success without waiting. The parent sleeps briefly, kills the child with SIGKILL, and waits.

State and persistence behavior: futex wait state is intentionally abandoned by a killed process. Rings and futex memory are not cleaned by the child.

Dependencies and integration points: targets futex cancellation/cleanup across process death, async workers, and SQPOLL.

Risks: signal timing is approximate. The test does not validate CQEs; it is a lifetime/crash regression.

Test signals: pass means all scalar/vectored async/SQPOLL combinations tolerate waiter death.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/futex-kill.c -->
