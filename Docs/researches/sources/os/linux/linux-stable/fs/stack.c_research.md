# File Research: sources/os/linux/linux-stable/fs/stack.c

## Summary
Provides helper functions for stackable filesystems to copy inode size/block accounting and inode attributes from lower to upper inodes.

## Key APIs
- `fsstack_copy_inode_size()`.
- `fsstack_copy_attr_all()`.

## Important Behavior
`fsstack_copy_inode_size()` reads `i_size` with `i_size_read()` and copies `i_blocks`, using `src->i_lock` on 32-bit-sized block counters and `dst->i_lock` when required to keep 64-bit `i_size` and/or `i_blocks` updates safe on 32-bit or preemptible/SMP systems.

`fsstack_copy_attr_all()` copies mode, uid/gid, rdev, atime/mtime/ctime, block bits, inode flags, and nlink.

## Risks
The helpers deliberately do not require `i_rwsem`. They avoid guaranteeing atomic consistency between `i_size` and `i_blocks`, which is acceptable for stackable filesystem attribute mirroring but not for quota-style accounting invariants.
