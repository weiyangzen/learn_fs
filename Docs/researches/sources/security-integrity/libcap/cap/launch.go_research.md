<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/launch.go -->
# sources/security-integrity/libcap/cap/launch.go

## Purpose
Launch support for running a callback and/or child process on a disposable locked OS thread with altered capability/security state.

## Important APIs, Types, And Functions
Defines `Launcher`, `NewLauncher`, `FuncLauncher`, `Callback`, `SetUID`, `SetGroups`, `SetMode`, `SetIAB`, `SetChroot`, `Launch`, and errors `ErrLaunchFailed`, `ErrNoLaunch`, `ErrAmbiguousChroot`, `ErrAmbiguousIDs`, and `ErrAmbiguousAmbient`.

## Control Flow
`Launch` copies launcher state under lock, starts `launch` in a goroutine, locks an OS thread distinct from the PID thread, marks launch-active state, optionally runs a callback, validates `ProcAttr`, applies UID/GID/mode/IAB/chroot changes on the single launch thread, calls `ForkExec`, then waits for the launch thread to die before re-enabling normal write syscalls.

## State And Persistence Behavior
Temporarily diverges one OS thread's credential/security state from the rest of the process. Child process inherits requested state. Package launch state maps active TIDs and blocks unrelated capability writes until cleanup.

## Dependencies And Integration Points
Works with `syscalls.go` launch-state synchronization, `oslocks.go`/`oslockluster.go` build tags, core Set/IAB/convenience APIs, and `syscall.ForkExec`.

## Risks And Edge Cases
This intentionally violates normal POSIX process-wide semantics for a narrow launch window. Incorrect callback syscalls can corrupt process state. Launch support depends on Go runtime behavior for terminating excess locked OS threads.

## Test Signals
Signals include `TestFuncLaunch`, callback error propagation, no securebit leakage to the parent, and explicit errors for ambiguous ProcAttr settings.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/launch.go -->
