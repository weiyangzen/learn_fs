# File Research: sources/os/linux/linux/fs/ufs/util.c

## Purpose
Implements UFS utility routines for reading multi-fragment metadata buffers, releasing/dirtying/syncing those buffers, encoding special-device inode data, and locking page-cache folios.

## Main Contents
- Metadata buffer helpers:
  - `_ubh_bread_()` allocates a `ufs_buffer_head` and reads up to `UFS_MAXFRAG` fragments.
  - `ubh_bread_uspi()` reuses the `ufs_sb_private_info` embedded superblock buffer.
  - `ubh_brelse()` and `ubh_brelse_uspi()` release buffer references.
  - `ubh_mark_buffer_dirty()`, `ubh_sync_block()`, `ubh_bforget()`, and `ubh_buffer_dirty()`.
- Device encoding helpers:
  - `ufs_get_inode_dev()` decodes special inode device numbers with Sun/Sun x86 special handling.
  - `ufs_set_inode_dev()` stores device numbers using SysV or old device encoding depending on UFS state flavor.
- Page-cache helper:
  - `ufs_get_locked_folio()` locks an existing folio or reads one, handles truncate races, and ensures buffers exist.

## Important Design Points
- UFS metadata can span several fragment-sized buffer_heads; `ufs_buffer_head` abstracts that group.
- Size validation requires fragment alignment and caps count at `UFS_MAXFRAG`.
- Sun and Sun x86 device fields differ: Sun x86 uses `i_data[1]`, most others use `i_data[0]`.
- `ufs_get_locked_folio()` creates empty buffers sized by `inode->i_blkbits` if the folio lacks buffers.

## Cross-File Relationships
- Declared by `util.h`.
- Uses `ufs_sb_private_info`, `ufs_buffer_head`, and UFS variant flags from `ufs_fs.h`/`ufs.h`.
- Device helpers are used by inode read/write and `namei.c` mknod paths.
- Folio helper supports block mapping/truncation paths elsewhere in UFS.

## Risks / Review Notes
- `_ubh_bread_()` allows `count == 0` if size is zero; `ubh_bread_uspi()` rejects it. Callers should not pass zero-size metadata reads.
- `ubh_bread_uspi()` failure releases buffers read so far but does not clear all slots after failure.
- `ufs_get_locked_folio()` returns `NULL` for truncate races and `ERR_PTR()` for read failures; callers must distinguish both.
