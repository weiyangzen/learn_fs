# File Research: sources/teaching/minix/minix/fs/ext2/mount.c

This file implements ext2 mount, unmount, and mountpoint marking.

Key entry points:
- `fs_mount(dev, flags, root_node, res_flags)`: opens block device, reads superblock, validates feature flags/state/root inode, sets LMFS block size/usage, and returns root node metadata.
- `fs_mountpt(ino_nr)`: validates a node can be used as a mountpoint and marks it.
- `fs_unmount()`: syncs, writes clean state, closes device, invalidates LMFS cache, and clears `s_dev`.

Important mount checks:
- Rejects unsupported incompatible and read-only-compatible features.
- Rejects `EXT2_ERROR_FS` state.
- Verifies root inode exists, has nonzero mode, and is a directory.
- Marks writable mounts as `EXT2_ERROR_FS` until clean unmount.

Notable bug risk:
- `fs_mountpt()` calls `put_inode(rip)` before setting `rip->i_mountpoint = TRUE`, potentially writing to an inode after reference release if the inode became unused.
