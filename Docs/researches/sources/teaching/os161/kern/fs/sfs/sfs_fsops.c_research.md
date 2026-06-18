# File Research: sources/teaching/os161/kern/fs/sfs/sfs_fsops.c

Implements SFS filesystem-level mount, sync, volume-name, and unmount operations.

Key components:
- Freemap I/O reads/writes all freemap blocks starting at `SFS_FREEMAP_START`.
- `sfs_sync` takes the VFS biglock, syncs all resident vnodes, writes the dirty freemap, then writes the dirty superblock.
- `sfs_getvolname` returns `sb_volname` under the biglock.
- `sfs_unmount` refuses if any vnode remains loaded, asserts clean superblock/freemap after prior VFS sync, drops the device pointer, and destroys the FS object.
- `sfs_fs_create` initializes the in-memory SFS object and compile-time checks on-disk structure sizes.
- `sfs_domount` validates device block size, reads and validates superblock magic, warns if FS block count exceeds device blocks, null-terminates volume name, allocates and reads freemap, and returns the abstract `struct fs`.
- `sfs_mount` delegates to `vfs_mount`.

Notable invariants:
- The free block bitmap includes rounded-up bits beyond the real device and expects `mksfs` to mark invalid sectors in use.
- SFS relies heavily on `vfs_biglock` for mount/sync/unmount consistency.
