# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_quota2.c

This small file mounts inode-based QUOTA2 files recorded in the FFS superblock.

Key responsibilities:
- Detect whether the filesystem requests QUOTA2.
- Validate quota magic and required user/group quota inode numbers.
- VGET quota inodes and attach them to `ufsmount`.
- Mark the mount as quota-enabled.

Important function:
- `ffs_quota2_mount`: If `FS_DOQUOTA2` is set, it enables `UFS_QUOTA2`, initializes quota block size/mask from the filesystem, validates `fs_quota_magic`, loads user/group quota vnodes according to `fs_quota_flags`, stores credentials, increments write counts, marks the group quota vnode as `VV_SYSTEM`, unlocks quota vnodes, and sets `MNT_QUOTA`.

Important interactions:
- Called from `ffs_mount` and `ffs_mountfs` for writable mounts when `QUOTA2` is compiled in.
- Uses quota inode numbers from `fs->fs_quotafile[]`.
- Cleanup is handled by quota2 unmount code in shared quota paths.

Notable behavior and risks:
- If group quota setup fails after user quota setup, it closes the user quota vnode before returning.
- User quota vnode write count is incremented but only group quota vnode is marked `VV_SYSTEM` in this code.
