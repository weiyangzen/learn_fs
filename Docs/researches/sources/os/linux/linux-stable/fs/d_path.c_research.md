# File Research: sources/os/linux/linux-stable/fs/d_path.c

## Summary
Implements kernel pathname string construction helpers and the `getcwd` syscall. It builds paths backward into caller buffers under RCU/sequence protection, handles concurrent rename and mount changes, supports synthetic dentry names, reports deleted or unreachable paths, and exports raw dentry path helpers.

## Main Responsibilities
- Provide a backward-growing `prepend_buffer` abstraction for path assembly.
- Safely copy dentry names that may race with rename using nofault kernel copies.
- Walk dentry and mount parent chains to construct paths relative to a root.
- Retry path construction under `rename_lock` and `mount_lock` sequence counters when races are detected.
- Implement `__d_path()`, `d_absolute_path()`, and exported `d_path()`.
- Support synthetic filesystem names through `dentry_operations::d_dname`.
- Provide `dynamic_dname()` and `simple_dname()` helpers for synthetic dentry naming.
- Implement raw and deleted-aware dentry path helpers.
- Implement `getcwd`, including unreachable path handling.

## Key APIs
- `__d_path()`
- `d_absolute_path()`
- `d_path()`
- `dynamic_dname()`
- `simple_dname()`
- `dentry_path_raw()`
- `dentry_path()`
- `SYSCALL_DEFINE2(getcwd)`

## Important Behavior
Path strings are prepended from the end of the supplied buffer. On overflow, the helpers preserve a suffix where possible and mark the buffer as failed so callers return `-ENAMETOOLONG`.

`prepend_name()` uses acquire loading for the name pointer and `READ_ONCE()` for length. Because pointer and length can be inconsistent during concurrent rename, `prepend_copy()` uses `copy_from_kernel_nofault()` and fills with `x` on fault; the sequence retry later discards raced output.

`prepend_path()` first attempts an RCU/sequence-count walk and falls back to locked sequence retry when rename or mount sequence counters require it. It distinguishes paths that reach the supplied root, absolute root, detached/not-yet-attached mounts, and escaped dentries.

`d_path()` appends `" (deleted)"` for unlinked dentries and delegates to `d_dname` for synthetic names unless the synthetic dentry is the mounted root. `getcwd` returns `(unreachable)` when the process working directory is outside its root.

## Research Notes
This file is concurrency-heavy VFS utility code. Its key invariants are dentry lifetime under RCU, race detection through global rename/mount sequence counters, safe handling of unstable names, and caller awareness that returned strings may start inside the provided buffer.
