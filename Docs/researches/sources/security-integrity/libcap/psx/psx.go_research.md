# sources/security-integrity/libcap/psx/psx.go

Purpose: non-cgo Go implementation of the psx package for Linux Go 1.16+.

Important APIs/functions: `Syscall3()` delegates to `syscall.AllThreadsSyscall()`, and `Syscall6()` delegates to `syscall.AllThreadsSyscall6()`. Build tags require `linux && !cgo && go1.16`.

Control flow: each wrapper directly returns Go's all-thread syscall result tuple. The file contains documentation aligning behavior with cgo mode while avoiding C linkage.

State and dependencies: no persistent package state. Depends on Go runtime support for all-thread syscalls and the `syscall` package.

Risks and test signals: limited to Go versions and Linux runtime semantics. Tests in `psx_test.go` and `psx_churn_test.go` exercise PID/error behavior and shared keepcaps state across goroutines/threads.
