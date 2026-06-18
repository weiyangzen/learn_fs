# File Research: sources/os/linux/linux/fs/ufs/util.h

## Purpose
Provides inline helpers and macros for endian-aware UFS field access, superblock/cylinder buffer addressing, directory entry manipulation, UID/GID conversion, bitmap operations, fragment accounting, UFS1/UFS2 block pointer handling, and timestamp generation.

## Main Contents
- Buffer-head accessors:
  - `UCPI_UBH()`, `USPI_UBH()`, `get_usb_offset()`
  - `ubh_get_usb_first()`, `ubh_get_usb_second()`, `ubh_get_usb_third()`
  - `ubh_get_ucg()`
- Variant-specific superblock access:
  - `ufs_get_fs_state()`, `ufs_set_fs_state()`
  - `ufs_get_fs_npsect()`
  - `ufs_get_fs_qbmask()`, `ufs_get_fs_qfmask()`
- Directory entry helpers:
  - `ufs_get_de_namlen()`, `ufs_set_de_namlen()`
  - `ufs_set_de_type()`
- UID/GID helpers:
  - `ufs_get_inode_uid()`, `ufs_set_inode_uid()`
  - `ufs_get_inode_gid()`, `ufs_set_inode_gid()`
- Function declarations for buffer utilities, device helpers, `ufs_prepare_chunk()`, and folio helpers.
- Byte/word access macros across multi-fragment metadata buffers:
  - `ubh_get_addr8/16/32/64()`
  - `ubh_get_data_ptr()`
  - `ubh_blkmap()`
- Free-space helpers:
  - `ufs_freefrags()`
  - cylinder-group array access macros.
  - bitmap set/clear/test/find helpers.
  - block-level bitmap helpers: `ubh_isblockset()`, `ubh_clrblock()`, `ubh_setblock()`.
  - `ufs_fragacct()` updates fragment summary accounting.
- UFS1/UFS2 data pointer helpers:
  - `ufs_get_direct_data_ptr()`
  - `ufs_data_ptr_to_cpu()`
  - `ufs_cpu_to_data_ptr()`
  - `ufs_data_ptr_clear()`
  - `ufs_is_data_ptr_zero()`
- `ufs_get_seconds()` returns filesystem-endian low 32 bits of current real time.

## Important Design Points
- Many macros rely on a caller-local `uspi` variable; this is a strong convention in UFS code.
- Directory entry length/type and UID/GID layouts are variant-specific and selected through `UFS_SB(sb)->s_flags`.
- UFS1 and UFS2 block pointers differ in width; pointer helper functions centralize that distinction.
- Bitmap search helpers work across fragmented `buffer_head` arrays rather than contiguous memory.
- `ufs_get_seconds()` intentionally wraps to 32 bits for superblock/cylinder-group timestamps so dirty-state detection remains compatible with UFS1-style fields.

## Cross-File Relationships
- Included by UFS implementation files for common low-level access.
- Depends on endian helpers from `swab.h` and structure definitions from `ufs_fs.h`.
- Used by `super.c` for superblock state, mask, summary, and time updates.
- Used by allocation/cylinder/inode/directory code for bitmap and pointer manipulation.

## Risks / Review Notes
- Comments on 44BSD directory name length say `XXX this seems wrong`; this is a known caution around raw byte versus endian-converted fields.
- Some address macros appear fragile and depend on correct shifts, fragment size fields, and local variable names.
- `find_last_zero_bit()` manually scans bytes and must be kept consistent with bitmap end/start semantics.
- `ufs_fragacct()` assumes fragment list indexing matches UFS fragment counts; accounting bugs here affect free-space summaries.
