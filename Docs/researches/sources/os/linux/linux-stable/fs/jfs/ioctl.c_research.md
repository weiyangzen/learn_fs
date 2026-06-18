# File Research: sources/os/linux/linux-stable/fs/jfs/ioctl.c

Implements JFS file attribute operations and the FITRIM ioctl.

Key pieces:
- `jfs_map_ext2()` maps between internal JFS inode flags and generic `FS_*` fileattr flags.
- `jfs_fileattr_get()` rejects special dentries and returns visible user flags from `mode2`.
- `jfs_fileattr_set()` rejects fsx attrs/special files/quota files, masks unsupported bits, updates `mode2`, propagates inode flags, ctime, and dirty state.
- `jfs_ioctl()` handles `FITRIM`: requires `CAP_SYS_ADMIN`, checks discard support, copies `fstrim_range`, normalizes `minlen`, calls `jfs_ioc_trim()`, and copies results back.

Integration:
- Fileattr hooks are referenced by `jfs_file_inode_operations`.
- FITRIM path delegates actual block selection/discard to `jfs_discard.c` and `jfs_dmap.c`.
