# File Research: sources/os/linux/linux-stable/fs/ufs/util.c

## Summary
Provides non-inline UFS utility routines for multi-fragment buffer-head handling, device number encoding/decoding, and page-cache folio acquisition.

## Key APIs
- `_ubh_bread_()`
- `ubh_bread_uspi()`
- `ubh_brelse()`
- `ubh_brelse_uspi()`
- `ubh_mark_buffer_dirty()`
- `ubh_sync_block()`
- `ubh_bforget()`
- `ubh_buffer_dirty()`
- `ufs_get_inode_dev()`
- `ufs_set_inode_dev()`
- `ufs_get_locked_folio()`

## Important Behavior
`_ubh_bread_()` allocates a `ufs_buffer_head` and reads a contiguous set of filesystem fragments; `ubh_bread_uspi()` performs the same read into the embedded superblock buffer in `ufs_sb_private_info`. Both require the requested size to align to fragment size and fit within `UFS_MAXFRAG`.

Buffer helpers release, mark dirty, synchronously write, forget, or test all buffer heads contained in a `ufs_buffer_head`.

Device encoding differs for Sun/Sun x86 variants. Sun-style special files may use SysV major/minor encoding, while other variants use old Linux device encoding. Sun x86 stores the device value in `i_data[1]`; other variants use `i_data[0]`.

`ufs_get_locked_folio()` locks an existing folio or reads it from disk, handles truncation races, and ensures buffer heads exist for the folio before returning it.

## Dependencies
Uses Linux buffer-head/page-cache APIs, UFS endian helpers, mount flavor flags, and UFS private inode structures.

## Risks
Partial read failures must release already-acquired buffers. Device encoding must match the filesystem flavor or special files will decode incorrectly. `ufs_get_locked_folio()` can return `NULL` for truncation races or an error pointer for read failures, so callers must distinguish both.
