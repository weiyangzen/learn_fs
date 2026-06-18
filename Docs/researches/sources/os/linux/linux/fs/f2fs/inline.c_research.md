# File Research: sources/os/linux/linux/fs/f2fs/inline.c

Read completely: 850 lines.

## Summary
Implements inline data and inline directory support. It decides when inline storage is valid, reads/writes inline file data from inode nodes, converts inline files/directories to regular block-backed layout, recovers inline data during roll-forward, supports inline directory lookup/mutation/readdir, and reports inline extents through fiemap.

## Main Responsibilities
- Determines whether a file, symlink, or directory may use inline storage.
- Validates inline-data consistency during inode sanity checks.
- Reads, writes, truncates, converts, and recovers inline file data.
- Converts inline directories to block-backed directories when they run out of inline slots.
- Adds, deletes, finds, checks emptiness, and reads inline directory entries.
- Emits inline fiemap extents.

## Key APIs
- Inline data policy: `f2fs_may_inline_data()`, `f2fs_sanity_check_inline_data()`, `f2fs_may_inline_dentry()`.
- Inline data I/O: `f2fs_read_inline_data()`, `f2fs_write_inline_data()`, `f2fs_truncate_inline_inode()`.
- Conversion/recovery: `f2fs_convert_inline_inode()`, `f2fs_convert_inline_folio()`, `f2fs_recover_inline_data()`.
- Inline directories: `f2fs_find_in_inline_dir()`, `f2fs_make_empty_inline_dir()`, `f2fs_try_convert_inline_dir()`, `f2fs_add_inline_entry()`, `f2fs_delete_inline_entry()`, `f2fs_empty_inline_dir()`, `f2fs_read_inline_dir()`.
- Reporting: `f2fs_inline_data_fiemap()`.

## Important Behavior
Inline data is allowed only for regular files and symlinks, not atomic-write users, and only while size fits `MAX_INLINE_DATA()`. Files requiring post-read processing, such as encryption/verity paths, are excluded from normal inline-data use.

`f2fs_convert_inline_folio()` reserves a real block, copies inline bytes to page cache, writes them out-of-place, waits for writeback, marks append-write recovery state, then clears inline data and flags. It treats a non-`NEW_ADDR` first block after reservation as corruption.

Inline recovery reconciles previous and recovered inline flags: keep inline data, drop inline data and recover blocks, truncate blocks and restore inline data, or recover normal blocks.

Inline directory conversion has two paths. Level-zero directories copy the inline dentry structure into a newly allocated dentry block. Rehashed directories back up inline dentries, clear inline storage, re-add entries through normal insertion, and restore the inline backup on failure.

Inline directory mutation updates the inode node directly, initializes new child inode metadata when needed, maintains parent metadata, and clears bitmap slots on delete.

`f2fs_inline_data_fiemap()` reports inline data as `FIEMAP_EXTENT_DATA_INLINE`, optionally syncing the inode node first, and computes the byte address relative to the inode node block when known.

## State and Synchronization
Uses inode-node folios, data folios, folio writeback waits, `f2fs_lock_op()`, inode `i_sem` for child metadata initialization, dirty inode/page accounting, inline xattr size compatibility state, and normal dentry helpers from `dir.c`.

## Risks
Inline conversion must preserve data while switching on-disk layout and recovery flags. Directory conversion can fail mid-rehash and must restore the inline dentry image. Inline-data sanity checks are important because inline flags must never coexist with real block pointers or incompatible inode types/features.
