# sources/security-integrity/libcap/psx/doc.go

Purpose: package-level Go documentation for `kernel.org/pub/linux/libs/security/libcap/psx`.

Important APIs described: `Syscall3` and `Syscall6` execute security-relevant syscalls on all threads. Documentation distinguishes non-cgo Go 1.16+ wrappers around `syscall.AllThreadsSyscall*` from cgo wrappers around C libpsx.

Control flow/integration: not executable beyond package declaration, but documents expected behavior: first thread performs syscall, failure returns immediately, success stops/synchronizes runtime so remaining threads perform it.

State and dependencies: explains dependency on Linux thread privilege semantics, Go runtime thread migration, cgo, and libpsx.

Risks and test signals: warns older Go toolchains may hang. The central risk is using regular syscalls for privilege drops in a multithreaded Go process. Tests in `psx_test.go`, `psx_cgo_test.go`, and churn tests cover this contract.
