# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_fileno.c

## Purpose

Manages pseudofs file number allocation for synthetic nodes.

## Main Entry Points

`pfs_fileno_init()` initializes the `pfs_info` mutex and creates an `unrhdr` allocator starting at file number 3. Root is reserved as file number 2.

`pfs_fileno_uninit()` deletes the allocator and destroys the mutex.

`pfs_fileno_alloc()` assigns:
- root: fixed file number 2.
- directories/files/symlinks/procdirs: a unique allocator number.
- `.`: the parent’s file number.
- `..`: the grandparent’s file number, or parent/root for root children.

`pfs_fileno_free()` releases allocator-owned file numbers and ignores root, `.`, and `..` nodes.

## Integration Points

Called from `pseudofs.c` during node add/destroy and filesystem init/uninit. `pseudofs_vnops.c` combines node file numbers with pid for process-dependent entries.

## Risks and Review Notes

The allocator range is bounded by `INT_MAX / NO_PID` because vnode file IDs may be multiplied by `NO_PID` and offset by pid for process-dependent nodes. Correct `.` and `..` numbering depends on parent links being established before allocation.
