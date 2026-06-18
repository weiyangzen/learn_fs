# File Research: sources/os/linux/linux/fs/d_path.c

## Summary
Implements kernel pathname rendering helpers and the `getcwd` syscall. It builds paths backward into caller buffers while handling RCU path walks, concurrent renames, mount traversal, detached paths, deleted dentries, synthetic dentry names, raw dentry paths, and user-copy for cwd.

## Main Responsibilities
- Provide backward-prepend buffer primitives.
- Safely copy dentry names under possible rename races.
- Walk dentries and mounts from a path back to a supplied root.
- Return pathnames relative to the process root or absolute root.
- Support synthetic filesystem `d_dname` callbacks.
- Format simple/dynamic dentry names for pseudo filesystems.
- Provide raw dentry-only paths.
- Implement `sys_getcwd`.

## Key APIs
- `__d_path()`
- `d_absolute_path()`
- `d_path()`
- `dynamic_dname()`
- `simple_dname()`
- `dentry_path_raw()`
- `dentry_path()`
- `getcwd` syscall

## Important Behavior
Path strings are constructed from the end of the buffer backward. Overflow sets the buffer length negative and returns `-ENAMETOOLONG` through `extract_string()`.

Name copying is intentionally tolerant of concurrent rename races. It uses optimistic loads and `copy_from_kernel_nofault()`; if a race produces a mismatched pointer/length and copying faults, the copied bytes are filled with `x`. Sequence checks on `rename_lock` and `mount_lock` decide whether to retry and discard such garbage.

`prepend_path()` handles mount roots by walking up to parent mounts, distinguishes absolute root, detached/not-attached paths, and escaped paths, and ensures `/` is emitted for root.

`d_path()` appends `" (deleted)"` for unlinked dentries and delegates to `d_dname` for synthetic dentries that are not mounted roots. `getcwd()` returns `(unreachable)` when the process cwd is outside its root, returns `-ENOENT` for unlinked cwd, and copies the final path to userspace.

## Research Notes
This file is concurrency-sensitive VFS utility code. Its central invariant is that optimistic path construction is acceptable only because rename/mount sequence counters force retries when concurrent mutations matter.
