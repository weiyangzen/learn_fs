<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/legacy.go -->
# sources/security-integrity/libcap/cap/legacy.go

## Purpose
Build-tag-specific syscall selection for older Linux architectures/toolchains using the 32-bit `setgroups32` syscall.

## Important APIs, Types, And Functions
Defines package variable `sysSetGroupsVariant = uintptr(syscall.SYS_SETGROUPS32)` under build tag `linux,386 arm mips mipsle`.

## Control Flow
No runtime control flow; it supplies the syscall number used by `SetGroups`.

## State And Persistence Behavior
No state beyond the package variable.

## Dependencies And Integration Points
Consumed by `convenience.go` `setGroups`.

## Risks And Edge Cases
Incorrect build tags or syscall number would break group changes on affected 32-bit platforms.

## Test Signals
Signals are successful `SetGroups` operation on legacy architectures.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/legacy.go -->
