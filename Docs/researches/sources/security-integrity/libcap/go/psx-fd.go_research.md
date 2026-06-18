## sources/security-integrity/libcap/go/psx-fd.go

Purpose: reproducer for older Go runtime deadlocks involving `AllThreadsSyscall` while another goroutine is blocked on a file descriptor.

Important APIs/functions: `os.Pipe`, goroutine `Read`, `time.Sleep`, and `psx.Syscall3(SYS_PRCTL, PR_SET_KEEPCAPS, ...)`.

Control flow: creates a pipe, starts a goroutine blocked reading, sleeps briefly to let it block, invokes psx all-thread `prctl`, then closes pipe descriptors.

State/persistence: toggles process `PR_SET_KEEPCAPS` during the test; no files.

Dependencies/integration: Go psx package, Go runtime thread/syscall behavior, Linux prctl. Built and run by `go/Makefile`, with timeout for known buggy Go versions.

Risks: intentionally can deadlock on Go 1.16/1.17 without cgo workaround; test result is runtime-version dependent.

Test signals: `timeout 5 ./psx-fd || echo "this is a known Go bug"` and cgo variant when `CGO_REQUIRED=0`.
