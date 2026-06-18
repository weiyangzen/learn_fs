# sources/user-network-fs/mergerfs/src/supported_statx.hpp

## Purpose
Detects build-time support for Linux `statx`.

## Important APIs, Types, and Functions
Defines `_GNU_SOURCE`, includes stat headers, and defines `MERGERFS_SUPPORTED_STATX` when `STATX_TYPE` is available.

## Control Flow
All behavior is controlled by preprocessor checks.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
Used by FUSE getattr/statx code to conditionally compile statx support.

## Risks and Edge Cases
Header-level `_GNU_SOURCE` can affect included libc declarations. Macro availability is compile-time only and does not prove syscall success.

## Test Signals
Compile on glibc/musl and non-Linux environments, plus runtime statx parity tests where enabled.
