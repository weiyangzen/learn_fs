<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/syscalls.go -->
# sources/security-integrity/libcap/cap/syscalls.go

## Purpose
Syscall dispatch and synchronization layer that preserves process-wide POSIX semantics while allowing temporary launcher-thread divergence.

## Important APIs, Types, And Functions
Defines `multisc`, `singlesc`, `launchState`, `launchIdle`, `launchActive`, `launchBlocked`, `scwMu`, `scwTIDs`, `scwState`, `scwCond`, `scwSetState`, and `scwStateSC`.

## Control Flow
Normal write syscalls use psx-backed all-thread calls. During launch, the launch TID can use single-thread syscalls while other writers block. `scwSetState` records launch TIDs and broadcasts state changes; `scwStateSC` waits for a safe writer state and returns the correct syscall adapter.

## State And Persistence Behavior
Maintains package-global synchronization state and active launch TID map. It controls when kernel credential/prctl writes are allowed.

## Dependencies And Integration Points
Depends on `kernel.org/pub/linux/libs/security/libcap/psx`, `runtime`, `sync`, and `syscall`. Used by all security-state writers.

## Risks And Edge Cases
Deadlocks or stale launch TIDs would block security writes. Inconsistent syscall selection during launch could panic pure-Go all-thread syscall implementations or leak thread-local privilege.

## Test Signals
Signals are launcher tests that mutate prctl state without leaking and normal capability APIs working during idle state.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/syscalls.go -->
