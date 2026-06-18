# File Research: sources/os/linux/linux/fs/ext4/ext4_jbd2.h

## Purpose

`ext4_jbd2.h` declares ext4’s journaling interface, transaction credit formulas, handle operation types, wrapper macros, inline JBD2 adapters, data journaling mode helpers, revoke credit helpers, direct-I/O journal compatibility checks, and journal teardown helper.

## Transaction Credit Model

- `EXT4_SINGLEDATA_TRANS_BLOCKS(sb)`
  - Estimates credits for modifying one data block.
  - Uses a larger estimate for extents-enabled filesystems.

- `EXT4_XATTR_TRANS_BLOCKS`
  - Credits for extended attribute metadata updates.

- `EXT4_DATA_TRANS_BLOCKS(sb)`
  - Combines single-data-block, xattr, and quota transaction needs.

- `EXT4_META_TRANS_BLOCKS(sb)`
  - Credits for superblock, inode, quota, and xattr metadata.

- `EXT4_MAX_TRANS_DATA`
  - Arbitrary maximum anticipated data blocks for large write/truncate transactions.

- `EXT4_RESERVE_TRANS_BLOCKS`
  - Low-credit threshold reserve used before extending or restarting large transactions.

- `EXT4_INDEX_EXTRA_TRANS_BLOCKS`
  - Extra credits for indexed directory insertion and htree splits.

- Quota credit macros:
  - `EXT4_QUOTA_TRANS_BLOCKS`
  - `EXT4_QUOTA_INIT_BLOCKS`
  - `EXT4_QUOTA_DEL_BLOCKS`
  - `EXT4_MAXQUOTAS_*`

## Handle Types

Defines numeric operation types for tracing/logging:

- `EXT4_HT_MISC`
- `EXT4_HT_INODE`
- `EXT4_HT_WRITE_PAGE`
- `EXT4_HT_MAP_BLOCKS`
- `EXT4_HT_DIR`
- `EXT4_HT_TRUNCATE`
- `EXT4_HT_QUOTA`
- `EXT4_HT_RESIZE`
- `EXT4_HT_MIGRATE`
- `EXT4_HT_MOVE_EXTENTS`
- `EXT4_HT_XATTR`
- `EXT4_HT_EXT_CONVERT`

## Declared APIs

- Inode dirtying and inode write reservation:
  - `ext4_mark_iloc_dirty()`
  - `ext4_reserve_inode_write()`
  - `__ext4_mark_inode_dirty()`
  - `ext4_expand_extra_isize()`

- Journal wrappers:
  - `__ext4_journal_get_write_access()`
  - `__ext4_forget()`
  - `__ext4_journal_get_create_access()`
  - `__ext4_handle_dirty_metadata()`
  - `__ext4_journal_start_sb()`
  - `__ext4_journal_stop()`
  - `__ext4_journal_start_reserved()`
  - `__ext4_journal_ensure_credits()`

## Wrapper Macros

- Macros inject `__func__` and `__LINE__` into lower-level functions:
  - `ext4_journal_get_write_access`
  - `ext4_forget`
  - `ext4_journal_get_create_access`
  - `ext4_handle_dirty_metadata`
  - `ext4_journal_stop`
  - `ext4_journal_start_reserved`

- Journal start convenience macros:
  - `ext4_journal_start_sb`
  - `ext4_journal_start`
  - `ext4_journal_start_with_reserve`
  - `ext4_journal_start_with_revoke`

## Inline Helpers

- `ext4_handle_valid(handle)`
  - Distinguishes real JBD2 handles from no-journal small-integer pseudo-handles.

- `ext4_handle_sync(handle)`
  - Marks a valid handle synchronous.

- `ext4_handle_is_aborted(handle)`
  - Checks aborted state only for valid JBD2 handles.

- `ext4_free_metadata_revoke_credits(sb, blocks)`
  - Accounts for metadata block freeing, scaling by cluster ratio.

- `ext4_trans_default_revoke_credits(sb)`
  - Default revoke credit estimate.

- `ext4_journal_extend()` / `ext4_journal_restart()`
  - No-op for no-journal handles; otherwise call JBD2.

- `ext4_journal_ensure_credits_fn(...)`
  - Ensures credits and can run a cleanup expression before transaction restart.
  - Returns negative error, zero for enough/extended credits, or one if restarted.

- `ext4_journal_ensure_credits(...)`
  - Simpler credit ensure wrapper.

- `ext4_journal_blocks_per_folio(inode)`
  - Delegates to JBD2 only when a journal exists.

- `ext4_journal_force_commit(journal)`
  - Forces commit if journal is non-null.

- `ext4_jbd2_inode_add_write()` / `ext4_jbd2_inode_add_wait()`
  - Adds ranged write/wait tracking to the inode’s JBD2 inode.

- `ext4_update_inode_fsync_trans()`
  - Records transaction IDs needed for fsync/fdatasync.

## Data Journaling Mode Helpers

- Modes:
  - `EXT4_INODE_JOURNAL_DATA_MODE`
  - `EXT4_INODE_ORDERED_DATA_MODE`
  - `EXT4_INODE_WRITEBACK_DATA_MODE`

- Predicates:
  - `ext4_should_journal_data()`
  - `ext4_should_order_data()`
  - `ext4_should_writeback_data()`

- `ext4_free_data_revoke_credits(inode, blocks)`
  - Returns zero for full data journaling and for non-journaled data.
  - For journaled data, accounts for blocks plus partial clusters at extent boundaries.

## Direct I/O Compatibility

- `ext4_should_dioread_nolock(inode)` allows direct I/O read without `i_rwsem` only when:
  - `DIOREAD_NOLOCK` mount option is set.
  - inode is regular.
  - inode uses extents.
  - data journaling is not enabled.
  - delayed allocation is enabled.

## Journal Teardown

- `ext4_journal_destroy(struct ext4_sb_info *sbi, journal_t *journal)`
  - Sets `EXT4_MF_JOURNAL_DESTROY`.
  - Forces a commit and flushes pending superblock update work.
  - Calls `jbd2_journal_destroy()`.
  - Clears `sbi->s_journal`.

## Dependencies

- Includes Linux VFS and JBD2 headers plus `ext4.h`.
- Depends on ext4 superblock state, quota feature helpers, inode journaling state, mount flags, and JBD2 transaction APIs.

## Research Notes

This header is the compile-time contract for all ext4 code that mutates metadata under journaling. Its credit formulas are conservative estimates that shape transaction sizing and restart behavior across inode, directory, xattr, quota, extent, resize, and truncate paths.
