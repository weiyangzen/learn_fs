# File Research: sources/os/linux/linux-stable/fs/ufs/util.h

## Summary
Defines inline UFS helpers for superblock field access, directory entry encoding, UID/GID conversion, buffer-head address arithmetic, bitmap operations, fragment accounting, block-pointer access, and timestamp conversion.

## Main Contents
- Buffer accessors: `UCPI_UBH()`, `USPI_UBH()`, `get_usb_offset()`, `ubh_get_usb_first/second/third()`, `ubh_get_ucg()`.
- Superblock state helpers: `ufs_get_fs_state()`, `ufs_set_fs_state()`, `ufs_get_fs_npsect()`, `ufs_get_fs_qbmask()`, `ufs_get_fs_qfmask()`.
- Directory entry helpers: `ufs_get_de_namlen()`, `ufs_set_de_namlen()`, `ufs_set_de_type()`.
- UID/GID helpers: `ufs_get_inode_uid()`, `ufs_set_inode_uid()`, `ufs_get_inode_gid()`, `ufs_set_inode_gid()`.
- Multi-fragment buffer declarations and address macros.
- Bitmap helpers: bit set/clear/test, next/last zero-bit search, full-block set/clear/test.
- Fragment accounting: `ufs_fragacct()`.
- Data pointer helpers for UFS1/UFS2: `ufs_get_direct_data_ptr()`, `ufs_data_ptr_to_cpu()`, `ufs_cpu_to_data_ptr()`, `ufs_data_ptr_clear()`, `ufs_is_data_ptr_zero()`.
- Time helper: `ufs_get_seconds()`.

## Important Behavior
State, qmask, npsect, directory name length, and UID/GID fields are layout-dependent and switch on flags set in `UFS_SB(sb)->s_flags`.

Bitmap helpers operate across fragmented `ufs_buffer_head` storage instead of one contiguous bitmap. Full-block helpers set or clear bit groups according to fragments-per-block values of 1, 2, 4, or 8.

UFS1 and UFS2 block pointers are abstracted through helpers that read/write either 32-bit or 64-bit on-disk fields depending on `fs_magic`.

`ufs_get_seconds()` intentionally wraps 32-bit superblock/cylinder timestamps instead of clamping, preserving UFS dirty-state logic through unsigned 32-bit time behavior.

## Dependencies
Uses UFS endian helpers, Linux bitmap helpers, UFS private geometry, and buffer-head/page-cache types.

## Risks
Many macros rely on an in-scope `uspi` variable. The comments mark 44BSD directory name length handling as suspicious. Bitmap address macros must stay synchronized with fragment size and buffer layout. Data pointer helpers must only be used after UFS1/UFS2 magic is known.
