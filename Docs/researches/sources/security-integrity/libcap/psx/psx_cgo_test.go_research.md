# sources/security-integrity/libcap/psx/psx_cgo_test.go

Purpose: cgo-specific errno regression test for Go psx wrappers.

Important APIs/functions: `TestErrno()` locks the OS thread, seeds C errno with `EPERM`, calls `Syscall3()` and `Syscall6()` with `SYS_GETUID`, compares return values, then verifies the original errno remains unchanged after successful syscalls.

Control flow: setup and cleanup happen under `runtime.LockOSThread()`, ensuring `setErrno()` and C calls refer to the same thread-local errno.

State and dependencies: mutates C errno for the locked thread. Depends on cgo build, syscall numbers, and psx wrappers.

Risks and test signals: catches accidental errno clobbering in the C bridge and mismatched 3-argument versus 6-argument behavior. It does not test failure errno directly beyond the helper semantics.
