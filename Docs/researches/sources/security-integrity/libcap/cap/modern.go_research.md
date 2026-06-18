<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/modern.go -->
# sources/security-integrity/libcap/cap/modern.go

## Purpose
Default syscall selection for modern platforms using `SYS_SETGROUPS`.

## Important APIs, Types, And Functions
Defines package variable `sysSetGroupsVariant = uintptr(syscall.SYS_SETGROUPS)` for Linux builds excluding legacy 32-bit variants.

## Control Flow
No runtime control flow; build tags select this file.

## State And Persistence Behavior
No mutable behavior beyond package initialization.

## Dependencies And Integration Points
Used by `convenience.go` when applying supplementary groups.

## Risks And Edge Cases
Wrong build-tag coverage would select an unsupported syscall on a platform.

## Test Signals
Signals are successful group-setting calls on modern platforms.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/modern.go -->
