# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext4/ext4_bh.c

This file provides the buffer-head operations used by the imported/ext4-style extent and xattr code. It adapts Linux buffer-head expectations to Ext2Fsd's backing buffer helpers.

`extents_bread` returns `sb_getblk(sb, block)` for reading or acquiring a buffer for an existing filesystem block. `extents_bwrite` returns `sb_getblk_zero(sb, block)`, giving callers a zeroed buffer for newly written metadata blocks. `extents_mark_buffer_dirty` marks a buffer dirty through `set_buffer_dirty`. `extents_brelse` releases a buffer with `brelse`. `extents_bforget` clears the buffer uptodate flag and then calls `bforget`, used when callers want to discard a dirty or invalid metadata buffer on error.

The file contains no policy logic. Its role is to keep Linux-derived extent/xattr routines independent of the underlying Windows cache-manager details. Callers rely on these wrappers for extent tree blocks, xattr blocks, and journal shim metadata writes.
