# sources/user-network-fs/mergerfs/src/supported_getdents64.hpp

## Purpose
Detects build-time support for the Linux `getdents64` syscall.

## Important APIs, Types, and Functions
Defines `MERGERFS_SUPPORTED_GETDENTS64` when compiling on Linux and `SYS_getdents64` is available from `<sys/syscall.h>`.

## Control Flow
Preprocessor-only feature detection.

## State and Persistence Behavior
No runtime state or persistence.

## Dependencies and Integration Points
Used by directory reading implementations to select `getdents64` code paths.

## Risks and Edge Cases
Availability of the syscall macro does not guarantee runtime behavior on every kernel or libc environment.

## Test Signals
Compile matrix tests on Linux and non-Linux targets should verify the macro is or is not defined as expected.
