# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufsmount.h

This header defines mount arguments, the common in-kernel `struct ufsmount`, filesystem dispatch operations, and UFS mount flags used by UFS-family filesystems.

Key responsibilities:
- Define userspace mount argument structures for UFS and MFS.
- Define the kernel-private mount state shared by FFS, LFS, ext2fs, and related UFS code.
- Store common device, superblock, quota, extended attribute, block geometry, symlink, directory, snapshot, and discard state.
- Define the `struct ufs_ops` method table for filesystem-specific operations.
- Provide macros that dispatch common UFS code to filesystem-specific implementations.
- Define UFS-specific mount flags, filesystem type IDs, quota transition flags, and byte-swap/format helpers.

Important structures:
- `struct ufs_args`: Block device path for UFS mounts.
- `struct mfs_args`: MFS mount parameters, including exported name, base address, and size.
- `struct ufsmount`: Holds mount pointer, device identifiers/vnode, filesystem type, flags, superblock union, extattr state, quota vnodes/credentials, indirect block geometry, quota v1/v2 state union, oldfs compatibility, max symlink length, directory block size, max file size, snapshot data, operation table, and discard data.
- `struct ufs_ops`: Filesystem-specific callbacks for inode times, update, truncate, balloc, snapshot gone, buffer read, and buffer write.

Important macros:
- `VFSTOUFS`: Converts `struct mount` to `struct ufsmount`.
- `UFS_OPS`, `UFS_ITIMES`, `UFS_UPDATE`, `UFS_TRUNCATE`, `UFS_BALLOC`, `UFS_SNAPGONE`, `UFS_BUFRD`, `UFS_BUFWR`: Common dispatch layer used throughout UFS code.
- `UFS_NEEDSWAP`, `UFS_ISAPPLEUFS`, `UFS_QUOTA`, `UFS_QUOTA2`, `UFS_EA`: UFS-specific mount flags.
- `UFS1`, `UFS2`: Filesystem type identifiers.
- `QTF_OPENING`, `QTF_CLOSING`: Quota v1 transition state.
- `MNINDIR`, `blkptrtodb`: Block mapping helpers.
- `FSFMT`: Tests whether old directory format without `d_type` is in use.

Important interactions:
- All files in this group depend on `ufsmount.h` for mount state and `UFS_*` dispatch.
- Concrete filesystems populate `um_ops`; common UFS code remains mostly filesystem-neutral.

Notable behavior:
- Quota v1 and quota v2 share storage through a union because their mount-level state differs.
- The superblock pointer is also a union so the same mount wrapper can support FFS, LFS, ext2fs, and CHFS-style users.
