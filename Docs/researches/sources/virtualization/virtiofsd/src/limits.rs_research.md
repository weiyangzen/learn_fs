# File Research: sources/virtualization/virtiofsd/src/limits.rs

## Scope

Open-file limit management for the daemon.

## APIs Covered

- Internal `get_max_nofile()` reads `/proc/sys/fs/nr_open`.
- Internal `get_nofile_limits()` wraps `getrlimit(RLIMIT_NOFILE)`.
- Internal `setup_rlimit_nofile_to()` wraps `setrlimit`.
- Public `setup_rlimit_nofile()` chooses and applies the limit.

## Behavior

- Default target is `1_000_000`, capped by `/proc/sys/fs/nr_open`.
- User value `0` leaves the current soft limit unchanged.
- If current soft limit is already at least the default, no change is made.
- Explicit user-supplied values above `nr_open` fail.
- If automatic default raising fails, it tries to fall back to the hard limit and warns.

## Role

Used by `main.rs` before computing guest FD quotas. Correct behavior is important because virtiofsd can hold many inode/file descriptors.
