<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chown.c -->
# sources/test-tools/stress-ng/stress-chown.c

## Purpose
Implements the `chown` stressor, exercising ownership changes on a shared temporary file through `fchown`, `chown`, and `lchown`.

## Important APIs, Types, and Functions
`stress_chown_info` exposes the stressor. `stress_chown_check()` ignores expected race/platform/permission errors. `do_fchown()` and `do_chown()` try combinations of current uid/gid, `(uid_t)-1`, `(gid_t)-1`, and root ownership probes when the worker lacks chown capability, restoring ownership if an unexpected root change succeeds.

## Control Flow
`stress_chown()` creates or opens a shared temp file, determines current uid/gid and whether effective uid is root, synchronizes, optionally queries `_PC_CHOWN_RESTRICTED`, then loops through fd, path, and lchown variants. It periodically fsyncs and increments bogo operations until stopped. Cleanup closes and removes the file and directory.

## State and Persistence Behavior
Runtime state is one temporary directory and file shared by worker instances plus an fd. It changes file ownership but restores or removes the file during cleanup. No repository state is persisted.

## Dependencies and Integration Points
Uses stress-ng temp file helpers, bad-fd helper, filesystem diagnostics, shim fsync/unlink/rmdir, process state, and bogo accounting. It integrates with normal worker synchronization so multiple instances contend on the same object.

## Risks and Edge Cases
Permissions dominate behavior: unprivileged users should see EPERM for root ownership, while root can perform more changes. Races with other instances can yield ENOENT. The retry loop for nonzero instances can return no-resource if the creator is delayed too long. Ownership changes on some filesystems may be restricted.

## Test Signals
Good signals are bogo progress without unexpected negative return codes, correct handling of EPERM for unprivileged users, and cleanup of the shared temp file. Run as both root and non-root when possible.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chown.c -->
