# sources/security-integrity/libcap/psx/psx_cgo.go

Purpose: cgo Go binding to the C libpsx all-thread syscall implementation.

Important APIs/functions: C helper `__errno_too()` reads/sets thread-local errno. Go `setErrno()` supports tests, `forceFatal()` sets `PSX_ERROR` sensitivity once, and `Syscall3()`/`Syscall6()` call `C.psx_syscall3/6`.

Control flow: each syscall wrapper forces fatal mismatch mode, locks the current goroutine to its OS thread to preserve errno association, calls the C function, and converts negative results into `syscall.Errno` using the C errno helper.

State and dependencies: package-level `sync.Once` controls sensitivity setup. Depends on cgo, `psx_syscall.h`, Go runtime thread locking, and C libpsx.

Risks and test signals: errno preservation and thread affinity are the core risks. A mismatch in C return behavior kills the program under PSX_ERROR. `psx_cgo_test.go` validates errno is preserved across successful calls and set on failure.
