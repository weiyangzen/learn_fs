# File Research: sources/os/linux/linux-stable/fs/ufs/ufs_fs.h

## Summary
Defines UFS on-disk format constants, superblock/cylinder/inode structures, filesystem flavor flags, and geometry macros used by the Linux UFS driver.

## Main Contents
- UFS/UFS2 magic values, superblock offsets, block/fragment constants, inode block indexes, root inode constants.
- Clean-state constants and flavor flags for directory entry, UID, state, cylinder-group, and UFS1/UFS2 encodings.
- Addressing macros for block/device conversion, cylinder group location, inode-to-block mapping, block/fragment rounding, and bitmap layout.
- Directory entry and cylinder summary structures.
- UFS1 and UFS2 inode structures.
- Cylinder group structures for modern and historic formats.
- `struct ufs_buffer_head`, `struct ufs_cg_private_info`, `struct ufs_sb_private_info`.
- Split superblock structures: `ufs_super_block_first`, `ufs_super_block_second`, `ufs_super_block_third`.

## Important Behavior
The header captures multiple UFS dialects in one set of structures. It separates the superblock into first/second/third chunks because the complete historical superblock can exceed a single 512-byte sector and is read through a multi-fragment `ufs_buffer_head`.

`ufs_sb_private_info` stores normalized, CPU-endian geometry and counters copied from disk at mount. Most runtime macros assume local variables named `uspi` and sometimes `sb`, so call sites must follow established UFS style.

UFS1 and UFS2 differ in block pointer width, superblock fields, timestamp width, cylinder summary placement, and maximum fast symlink storage. The header encodes these differences through unions and flavor flags.

## Dependencies
Used by all UFS files plus `swab.h`/`util.h`. Relies on Linux integer, stat, fs, workqueue, and division helpers.

## Risks
Structure definitions must match disk layout exactly. Several macros depend on caller-local variable names and derived mount geometry. UFS dialect flags must be set correctly during mount before interpreting directory entries, UID fields, state fields, and cylinder-group data.
