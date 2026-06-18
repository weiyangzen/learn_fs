## sources/security-integrity/libcap/go/psx-signals.go

Purpose: validates psx all-thread syscalls do not spuriously interact with Go signal handling.

Important APIs/functions: `signal.Notify`, `psx.Syscall3(SYS_PRCTL, PR_SET_KEEPCAPS, ...)`, and timed select.

Control flow: subscribes to interrupt signals, toggles `KEEP_CAPS` ten times via psx syscall, then waits one second and fails if any signal arrives.

State/persistence: mutates process `PR_SET_KEEPCAPS` flag repeatedly; no persistent files.

Dependencies/integration: Go psx package, Go signal package, Linux prctl. Built/run by `go/Makefile` test, including cgo variant where needed.

Risks: only observes a one-second window; ambient environment signals can cause false failure.

Test signals: successful `./psx-signals` output ending in `PASSED`; cgo/non-cgo matrix.
