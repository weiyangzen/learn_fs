# File Research: sources/os/linux/linux/fs/ufs/ufs.h

## Purpose
Central internal UFS header for Linux. It defines in-memory superblock and inode-private structures, mount option flags, debug macros, cross-file prototypes, and common conversion helpers.

## Main Contents
- `struct ufs_sb_info`: per-mounted-filesystem state, including private superblock info, cylinder summaries, cylinder-group buffers/cache slots, byte order, flavor flags, error policy, delayed sync work, and mount lock.
- `struct ufs_inode_info`: UFS inode extension with UFS1/UFS2 block-pointer storage, fast symlink storage, flags, shadow fields, last fragment, metadata seqlock, truncate mutex, directory lookup hint, and embedded VFS inode.
- Mount flags:
  - Error policy: panic, lock, umount, repair.
  - UFS flavor: old, 44BSD, Sun, NeXTstep, NeXTstep CD, OpenStep, Sun x86, HP, UFS2, SunOS.
- `UFSD()` debug macro under `CONFIG_UFS_DEBUG`.
- Prototypes for UFS allocation, cylinder, directory, file, inode, and superblock code.
- Accessors:
  - `UFS_SB()` maps `super_block` to `ufs_sb_info`.
  - `UFS_I()` maps VFS inode to `ufs_inode_info`.
  - `ufs_dtog()` and `ufs_dtogd()` compute cylinder group number and offset for a filesystem block.

## Important Design Points
- This header is the internal dependency hub for the UFS driver.
- `ufs_inode_info.i_u1` supports both 32-bit UFS1 block pointers and 64-bit UFS2 pointers, plus fast symlink storage sized for the larger case.
- Delayed superblock sync state is embedded in `ufs_sb_info` and protected by `work_lock`.
- `s_lock` is the coarse superblock lock used around mount/remount/statfs/sync-sensitive state.

## Cross-File Relationships
- Included by most UFS implementation files.
- Depends on layout definitions from `ufs_fs.h`.
- Prototypes functions implemented in `balloc.c`, `cylinder.c`, `dir.c`, `file.c`, `ialloc.c`, `inode.c`, `namei.c`, and `super.c`.

## Risks / Review Notes
- Changes to `struct ufs_inode_info` affect slab cache construction in `super.c`, including usercopy whitelisting for fast symlink storage.
- Mount flavor flag values are also used as parser enum results in `super.c`; changing them affects option handling.
- `ufs_dtog()` and `ufs_dtogd()` mutate their local copy through `do_div`; callers are safe only because arguments are passed by value.
