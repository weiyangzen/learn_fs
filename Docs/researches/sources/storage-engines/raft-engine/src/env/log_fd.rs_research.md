# sources/storage-engines/raft-engine/src/env/log_fd.rs

## Purpose
Selects the concrete low-level log file descriptor implementation for the current target and feature set.

## Important APIs, Types, And Functions
Re-exports `unix::LogFd` when not Windows and `std_fs` is not enabled; otherwise re-exports `plain::LogFd`.

## Control Flow
Compilation-time `cfg` gates choose the module. There is no runtime branch.

## State And Persistence Behavior
Persistence semantics depend on the selected implementation. Unix uses raw file descriptors and positional I/O; plain uses synchronized standard `File` handles.

## Dependencies And Integration Points
Integrated by `env/default.rs`, which imports `crate::env::log_fd::LogFd`. The `std_fs` feature in Cargo and platform target decide which backend backs all default file operations.

## Risks And Edge Cases
Different implementations can have subtle performance and sync behavior differences. CI's feature matrix includes `std_fs` to catch fallback-specific regressions.

## Test Signals
Compilation on supported targets and `std_fs` feature test runs validate module selection.
