# File Research: sources/os/linux/linux/fs/stack.c

Provides helper exports for stackable filesystems.

`fsstack_copy_inode_size()` copies `i_size` and `i_blocks` from a lower inode to an upper inode. It accounts for 32-bit SMP/preemption constraints by taking locks only when field width requires synchronization.

`fsstack_copy_attr_all()` copies mode, uid/gid, rdev, atime/mtime/ctime, block bits, flags, and link count.

Both functions are exported GPL symbols for filesystem stacking users.
