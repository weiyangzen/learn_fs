# sources/user-network-fs/mergerfs/src/procfs.cpp

## Purpose
Manages cached `/proc` directory handles and exposes thread/process metadata helpers.

## Important APIs, Types, and Functions
`procfs::init()` opens `/proc` and, on Linux, `/proc/self/fd` as `O_PATH` directory fds. `procfs::shutdown()` closes them. `procfs::get_name(tid)` reads `/proc/<tid>/comm` through the cached proc fd.

## Control Flow
Initialization is idempotent and aborts through `fatal::abort()` on required open failures. `get_name()` requires initialization, formats a relative path, opens it with `openat`, reads up to 255 bytes, strips a trailing newline, and returns an empty string on read/open failure.

## State and Persistence Behavior
State is process-global file descriptors `g_PROCFS_DIR_FD` and `procfs::PROC_SELF_FD_FD`. No filesystem content is modified.

## Dependencies and Integration Points
Depends on mergerfs `fs_*` wrappers, `fmt`, scope guards, and Linux procfs. Other low-level code can use `PROC_SELF_FD_FD` for fd-path operations.

## Risks and Edge Cases
The helper is Linux/procfs-specific in practice. `fmt::format_to_n` truncation is not explicitly checked for very large tids. Calling before `init()` aborts the process.

## Test Signals
Test init/shutdown idempotency, current thread name lookup, missing tid behavior, and Linux/non-Linux compilation paths.
