# sources/security-integrity/libcap/psx/psx_test.go

Purpose: Go tests for psx syscall wrappers in cgo and non-cgo builds.

Important APIs/functions: `TestSyscall3()` and `TestSyscall6()` validate `GETPID` success and malformed `CAPGET` failure errno. `killAThread()` creates an OS-thread churn helper. `TestShared()` repeatedly toggles `PR_SET_KEEPCAPS`, starts locked-thread trackers, and verifies all trackers observe the new state.

Control flow: `TestShared()` serializes tracker goroutines through channels so each reads keepcaps after each process-wide change.

State and dependencies: mutates process keepcaps and creates locked OS threads. Depends on syscall constants and package `Syscall3/6`.

Risks and test signals: catches wrapper return-value handling, errno mapping, all-thread state propagation, and runtime thread migration regressions.
