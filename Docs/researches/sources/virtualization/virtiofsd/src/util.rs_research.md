# File Research: sources/virtualization/virtiofsd/src/util.rs

## Purpose

This file provides utility functions for pid files, safer fork behavior, child waiting, capability manipulation, and lightweight error-context helpers used across virtiofsd.

## Main Functions And Traits

- `try_lock_file(file)`: acquires a non-blocking exclusive `flock`.
- `write_pid_file(pid_file_name)`: creates, locks, verifies, and writes the current process ID to a pid file.
- `pidfd_open(pid, flags)`: raw syscall wrapper for `pidfd_open`.
- `sfork()`: forks while arranging parent-death detection for the child.
- `wait_for_child(pid) -> !`: drops parent capabilities, waits for a child, and exits with the child’s status.
- `add_cap_to_eff(cap_name)`: adds a named Linux capability to the effective set using `capng`.
- `other_io_error(err)`: compatibility helper for `io::ErrorKind::Other`.
- `ErrorContext`: trait to prepend context to an `io::Error`.
- `ResultErrorContext`: trait to lazily add context to `Result` errors.

## PID File Handling

`write_pid_file()` loops until it can safely lock the actual current pid file path:

1. Opens/creates the file with mode `0600` and `O_CLOEXEC`.
2. Acquires `LOCK_EX | LOCK_NB`.
3. Compares the inode of the locked file descriptor with the inode currently reachable at the path.
4. Retries if the path was removed or replaced during the race.
5. Writes the current PID and returns the open file, keeping the lock alive.

This avoids stale locks on files that have been unlinked and replaced.

## Safe Fork Flow

`sfork()` uses `pidfd_open(getpid(), 0)` before `fork()` to hold a stable reference to the original parent. In the child:

1. It calls `prctl(PR_SET_PDEATHSIG, SIGTERM)` so the child receives SIGTERM if the parent dies.
2. It polls the parent pidfd with timeout 0 to detect whether the parent died before `prctl()` was set.
3. If the pidfd is readable, it returns an error indicating unexpected parent death.

The parent and child both return the `fork()` result like normal `fork`: child sees `0`, parent sees child PID.

## Child Waiting

`wait_for_child(pid)` clears all capabilities in the waiting parent, applies the change, waits for the child with `waitpid`, and exits with:

- the child exit code if it exited normally,
- negative signal number if it was signaled,
- failure for unexpected wait status or waitpid failure.

This function never returns.

## Capability Helper

`add_cap_to_eff(cap_name)` resolves a capability name without `CAP_`, refreshes process capabilities, adds it to the effective set, and applies the capability set.

## Error Helpers

`other_io_error()` exists because `io::Error::other()` was too new for this project’s target Rust version.

`ErrorContext` and `ResultErrorContext` allow code to add displayable context while preserving an `io::Error` kind. `soft_idmap/mod.rs` uses `err_context()` to attach the originating map entry to construction errors.

## Integration Points

This module is used by:

- `sandbox.rs` for `sfork()`, `wait_for_child()`, and contextual IO errors.
- `vhost_user.rs` and other modules through `other_io_error`.
- `soft_idmap/mod.rs` through `ResultErrorContext`.
- daemon startup code for pid files and capabilities.

## Risks And Edge Cases

- `sfork()` depends on `pidfd_open`, so it requires a kernel with that syscall.
- `wait_for_child()` exits the process and should only be called in a parent supervisory path.
- `write_pid_file()` returns an error if another process already holds the lock; it does not wait.
- `ErrorContext` recreates an `io::Error` with the same kind but a formatted string, so original OS error metadata beyond kind is not preserved.
