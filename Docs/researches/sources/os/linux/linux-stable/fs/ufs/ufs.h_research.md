# File Research: sources/os/linux/linux-stable/fs/ufs/ufs.h

## Summary
Defines UFS in-core superblock/inode state, mount option constants, debug macros, cross-file function prototypes, and helper accessors.

## Main Contents
- `struct ufs_sb_info`: per-mount state, flavor/byte-order flags, cylinder-group caches, delayed sync work, and mount lock.
- `struct ufs_inode_info`: UFS private inode data, direct/indirect block storage, fast symlink buffer, metadata lock, truncate mutex, and embedded VFS inode.
- Mount option constants for error policy and UFS flavor.
- Debug macro `UFSD()`.
- Prototypes for allocation, cylinder, directory, file, inode, namei, and superblock helpers.
- Accessors `UFS_SB()`, `UFS_I()`.
- Geometry helpers `ufs_dtog()` and `ufs_dtogd()`.

## Important Behavior
`ufs_sb_info` is the central in-memory mount object and stores both user-selected flavor and derived flags from `ufs_fs.h`. `ufs_inode_info.i_u1` abstracts UFS1 32-bit block pointers, UFS2 64-bit block pointers, and fast symlink storage in the same space.

## Dependencies
Included throughout UFS code. Depends on Linux inode/superblock types, workqueues, buffer heads, seqlocks, and UFS on-disk definitions.

## Risks
The shared union in `ufs_inode_info` must be interpreted consistently with UFS1/UFS2 magic and inode type. The header exposes many cross-file contracts, so layout or prototype drift affects the entire UFS implementation.
