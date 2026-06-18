<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/oslocks.go -->
# sources/security-integrity/libcap/cap/oslocks.go

## Purpose
Go-1.10+ launch support validation for child process attributes.

## Important APIs, Types, And Functions
Defines `LaunchSupported = true` and `validatePA(pa *syscall.ProcAttr, chroot string)`.

## Control Flow
If no `SysProcAttr` exists and chroot is requested, it creates one. It rejects callback-supplied chroot, credentials, or ambient caps that conflict with `Launcher` configuration.

## State And Persistence Behavior
May mutate the pending `ProcAttr` by assigning `SysProcAttr.Chroot`; it does not mutate process state.

## Dependencies And Integration Points
Used by `launch.go` before applying launch credentials and calling `ForkExec`.

## Risks And Edge Cases
Validation prevents ambiguous authority, but callbacks can still make other unsafe process-state changes.

## Test Signals
Signals are successful launch on supported Go and explicit ambiguous-configuration errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/oslocks.go -->
