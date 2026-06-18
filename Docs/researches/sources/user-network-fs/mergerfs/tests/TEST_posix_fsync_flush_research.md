# sources/user-network-fs/mergerfs/tests/TEST_posix_fsync_flush

## Purpose
Compares fsync/flush semantics for files, directories, bad descriptors, and final content.

## Important APIs, Types, and Functions
The script is a standalone Python test with a `main()` entrypoint. It primarily uses `posix_parity.mergerfs_mount()` to create an isolated mounted pool and helper functions such as `compare_calls`, `fail`, `touch`, `cleanup_dir`, `temp_dir`, option xattr helpers, or direct `os`/`ctypes` syscalls depending on the case.

## Control Flow
The test mounts mergerfs in a context manager, prepares mounted and sometimes native comparison paths, performs the target filesystem operations, and returns `0` on success, `1` on semantic mismatch, or `77` when the environment lacks required support. Cleanup runs in `finally` blocks.

## State and Persistence Behavior
State is limited to temporary test directories, branch contents, open file descriptors, runtime mergerfs options, and transient xattrs. Files and mounts are removed after the test unless the process is interrupted.

## Dependencies and Integration Points
Depends on the shared `posix_parity.py` harness, a working mergerfs binary, FUSE unmount tooling, and OS support for the specific syscall or option under test. It integrates with `tests/run-tests`.

## Risks and Edge Cases
Some behavior is platform, filesystem, privilege, or kernel dependent, so the script skips when prerequisites are absent. Race-oriented and descriptor-after-unlink cases are sensitive to cleanup and fd lifetime correctness.

## Test Signals
Important signals are exact errno parity, matching return values or metadata/content where compared, no leaked mount state, correct skip code for unsupported environments, and stable behavior across repeated runs.
