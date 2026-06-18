<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/seccomp/explore.go -->
# sources/security-integrity/libcap/contrib/seccomp/explore.go

## Purpose
Go seccomp experiment showing that seccomp filter application with TSYNC mirrors restrictions across threads and comparing raw prctl with psx-mediated prctl.

## Important APIs, Types, And Functions
Defines flags `--psx`, `--delays`, `--kill`, `--errno`, BPF structs `SockFilter` and `SockFProg`, filter constructors, `prctl`, `SeccompSetModeFilter`, `lockProcessThread`, `applyPolicy`, and `main`.

## Control Flow
Builds a BPF program that validates architecture, loads syscall number, traps or errno-blocks `setuid`, and allows everything else. It sets no-new-privs, applies seccomp TSYNC, locks to the PID thread, attempts `setuid(1)`, and reports whether the syscall was blocked or faked.

## State And Persistence Behavior
Mutates no-new-privs and seccomp filter state for the process; these are irreversible for the process lifetime. With `--delays`, sleeps expose inspection windows.

## Dependencies And Integration Points
Uses raw Linux syscalls, hard-coded x86_64 seccomp syscall number and audit arch, Go runtime thread locking, and optional libcap `psx` syscall wrapper.

## Risks And Edge Cases
Architecture constants are hard-coded and comments mark some offsets as not fully understood. Running with default kill/trap behavior can terminate the process. Seccomp/no-new-privs cannot be undone.

## Test Signals
Signals are expected fatal blocked `setuid`, errno-return behavior, fake-success with unchanged UID, and differences between raw and psx prctl setup paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/seccomp/explore.go -->
