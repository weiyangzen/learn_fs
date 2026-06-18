<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/convenience.go -->
# sources/security-integrity/libcap/cap/convenience.go

## Purpose
Convenience APIs for securebits, libcap security modes, UID/GID changes, and prctl wrappers with process-wide POSIX semantics.

## Important APIs, Types, And Functions
Defines `Secbits`, securebit constants, `GetSecbits`, `(Secbits).Set`, `Mode`, mode constants, `GetMode`, `(Mode).Set`, `SetUID`, `SetGroups`, `Prctlw`, and `Prctl`.

## Control Flow
Mode detection reads securebits, ambient bits, process sets, and bounding bits. Mode setting temporarily raises `SETPCAP`, sets securebits, optionally clears ambient/bounding/permitted state, and lowers effective caps on return. UID/GID helpers temporarily raise `SETUID` or `SETGID`, perform syscalls, and lower effective caps afterward.

## State And Persistence Behavior
These functions mutate process credential and securebit state across all OS threads via `scwStateSC`. Some operations, especially `ModeNoPriv` and bounding drops, are irreversible for the process.

## Dependencies And Integration Points
Uses constants from Linux prctl/securebits APIs, `sysSetGroupsVariant` from build-tag files, core `Set` operations, and the syscall synchronization layer.

## Risks And Edge Cases
Security mode changes can fail due to locked securebits or missing capabilities and may partially alter state. Dropping bounding bits cannot be undone. `SetUID`/`SetGroups` assume capability availability rather than root semantics.

## Test Signals
Signals include mode string output, successful prctl wrapper behavior, and tests/examples that verify capability lowering and launcher isolation.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/convenience.go -->
