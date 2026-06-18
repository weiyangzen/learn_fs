# File Research: sources/os/linux/linux/fs/ufs/ufs_fs.h

## Purpose
Defines the UFS on-disk format, layout constants, compatibility flags, cylinder group structures, inode structures, and private derived geometry structures used by the Linux UFS driver.

## Main Contents
- On-disk endian typedefs: `__fs16`, `__fs32`, `__fs64`.
- Core constants:
  - Boot/superblock offsets and sizes.
  - UFS1/UFS2 and HP magic values.
  - block/fragment sizing, direct/indirect block counts, root inode, clean-state values, and maximum directory name/link limits.
- Variant flag masks:
  - Directory entry format: old versus 44BSD.
  - UID/GID format: old, 44BSD, EFT.
  - State encoding: old, 44BSD, Sun, SunOS, Sun x86.
  - Cylinder group encoding: old, Sun, 44BSD.
  - Filesystem type: UFS1 versus UFS2.
- Geometry macros:
  - filesystem-block to disk-block conversion.
  - cylinder group base/super/cg/inode/data locations.
  - inode number to cylinder group/block/offset.
  - fragment/block rounding and mask helpers.
- Directory and summary structures:
  - `struct ufs_dir_entry`
  - `struct ufs_csum`
  - `struct ufs2_csum_total`
  - `struct ufs_csum_core`
- Superblock layouts:
  - Historical full `struct ufs_super_block` is retained in `#if 0` as documentation.
  - Active split layouts: `ufs_super_block_first`, `ufs_super_block_second`, `ufs_super_block_third`.
- Cylinder group layouts:
  - `struct ufs_cylinder_group`
  - `struct ufs_old_cylinder_group`
  - magic and old-format access macros.
- Inode layouts:
  - `struct ufs_inode` for UFS1 variants.
  - `struct ufs2_inode` for UFS2 with 64-bit size/timestamps/block pointers.
  - BSD inode flag constants.
- In-memory support structures:
  - `struct ufs_buffer_head`
  - `struct ufs_cg_private_info`
  - `struct ufs_sb_private_info`

## Important Design Points
- This file is a compatibility boundary. It models multiple historical UFS dialects in one driver.
- The active superblock representation is split into 512-byte pieces because a full superblock may span several fragments/buffers.
- Many macros assume a local variable named `uspi`, and some also assume `sb`; callers must follow the established local naming convention.
- UFS2 uses 64-bit block pointers and summary values, while UFS1 variants mostly use 32-bit fields.
- `ufs_sb_private_info` stores normalized, CPU-native derived values so runtime code does not repeatedly decode every on-disk superblock field.

## Cross-File Relationships
- Included by all UFS C files and internal headers.
- `super.c` fills `ufs_sb_private_info` from the split superblock structures and uses variant flags defined here.
- `util.h` uses directory, inode, bitmap, and superblock field definitions to implement endian-aware accessors.
- `namei.c` uses `UFS_MAXNAMLEN`, symlink sizing, and inode constants.
- Allocation, inode, directory, and cylinder code rely on cylinder group and bitmap layout definitions.

## Risks / Review Notes
- On-disk structure edits can break compatibility with existing UFS images.
- Several comments document historical oddities, such as HP flag overlap and variant-specific field reuse.
- The `ufs_cbtorpos()` macro is complex and variant-sensitive; allocation code depending on rotational layout should be treated carefully.
- Bitwise typedefs help catch endian mistakes, but many accesses still depend on correct helper usage.
