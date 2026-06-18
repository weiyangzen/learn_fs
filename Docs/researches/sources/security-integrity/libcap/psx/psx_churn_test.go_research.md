# sources/security-integrity/libcap/psx/psx_churn_test.go

Purpose: Go regression test for PSX behavior during thread churn, especially around Go issue 42494.

Important APIs/functions: `TestThreadChurn()` loops through combinations of killing locked OS threads and issuing PSX `prctl(PR_SET_KEEPCAPS)` syscalls.

Control flow: for each mode, it counts down from 50; optionally starts a goroutine that locks to an OS thread and exits after channel close, and optionally performs an all-thread keepcaps syscall.

State and dependencies: mutates process keepcaps state and relies on Go runtime thread creation/destruction. Uses `killAThread()` from `psx_test.go`.

Risks and test signals: catches hangs, missed threads, or signal/runtime conflicts when threads appear/disappear during PSX operations. This is a concurrency stress signal rather than a semantic capability comparison.
