<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/fd.go -->
# sources/security-integrity/libcap/cap/fd.go

## Purpose
Go 1.12+ helper for extracting an `os.File` descriptor without incurring Go runtime thread-pinning side effects from direct `File.Fd()` use.

## Important APIs, Types, And Functions
Defines `fd(file *os.File) uintptr` using `file.SyscallConn()` and `RawConn.Control`.

## Control Flow
Gets a syscall connection, returns all-bits-one on error, otherwise captures the descriptor passed to the control callback.

## State And Persistence Behavior
Does not mutate file or process state. It only observes the descriptor while under runtime-managed control.

## Dependencies And Integration Points
Used by `GetFd` and `SetFd` in `file.go` for fgetxattr/fsetxattr operations.

## Risks And Edge Cases
If `SyscallConn` fails, callers receive an invalid descriptor value and the subsequent syscall should fail. The helper assumes the descriptor remains valid for the immediate syscall use.

## Test Signals
Signals are file capability tests passing without runtime thread-lock leakage.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/fd.go -->
