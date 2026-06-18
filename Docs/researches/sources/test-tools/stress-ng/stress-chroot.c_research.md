<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chroot.c -->
# sources/test-tools/stress-ng/stress-chroot.c

## Purpose
Implements the `chroot` stressor, testing valid and invalid `chroot()` behavior and checking for known escape patterns using `chdir("..")` and saved cwd file descriptors.

## Important APIs, Types, and Functions
`stress_chroot_info` registers the stressor with a `CAP_SYS_ADMIN` support check when `chroot()` is available. `chroot_shared_data_t` stores shared metrics, escape flags, root inode, and cwd fd. `do_chroot()` times successful `chroot()` calls and always follows with `chdir("/")`. Nine test functions cover valid chroot, bad pointers, long/nonexistent/file/device paths, huge paths, and two escape checks.

## Control Flow
`stress_chroot()` mmap's shared data, creates a temp chroot directory and a file target, stores a cwd fd, synchronizes, then repeatedly forks a child to run the next test function. The parent waits and fails on nonzero child status, increments bogo count on success, rotates through tests, reports escape methods from shared flags, records a chroot-rate metric, and cleans all temp objects.

## State and Persistence Behavior
Temporary state includes shared mmap metrics, global path buffers, a temp chroot directory, a file used for ENOTDIR checks, and an fd to the original cwd. Each actual `chroot()` happens in a forked child so the parent process remains outside the jail for continued testing and cleanup.

## Dependencies and Integration Points
Uses stress-ng capability checks, mmap helpers, temp file helpers, OOM/scheduling helpers in children, wait handling, metrics, and filesystem wrappers. It is only implemented on platforms with `chroot()`.

## Risks and Edge Cases
Requires high privilege and intentionally explores security-sensitive behavior. Children must chdir after chroot to avoid unsafe cwd semantics. Escape detection is informational but important. Some kernels/filesystems return EPERM/ENOENT instead of ENOTDIR for certain paths. Failure to isolate tests in children would trap the worker inside a chroot.

## Test Signals
Expected signals are skip without CAP_SYS_ADMIN, successful cycling through child tests when privileged, optional informational escape reports, nonzero "chroot calls per sec", and cleanup of temp directory/file.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chroot.c -->
