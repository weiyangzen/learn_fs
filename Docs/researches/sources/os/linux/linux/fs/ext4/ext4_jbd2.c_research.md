# File Research: sources/os/linux/linux/fs/ext4/ext4_jbd2.c

## Purpose

`ext4_jbd2.c` implements ext4’s runtime wrapper layer around JBD2. It selects inode data journaling mode, starts/stops journal handles, supports no-journal pseudo-handles, ensures transaction credits, assigns metadata checksum triggers, forgets/revokes buffers, and marks metadata dirty.

## Main Functions

- `ext4_inode_journal_mode(struct inode *inode)`
  - Chooses one of:
    - journal data
    - ordered data
    - writeback data
  - Returns writeback if no journal exists.
  - Uses journal data for non-regular files, EA inodes, full data journaling mount mode, or `EXT4_INODE_JOURNAL_DATA` without delayed allocation.
  - Encrypted regular file data is not fully journaled and falls back to ordered mode.
  - Uses mount `DATA_FLAGS` for ordered/writeback decisions.

- `ext4_get_nojournal()` / `ext4_put_nojournal()`
  - Implement no-journal nesting using small integer pseudo-handles stored in `current->journal_info`.
  - Guarded by `EXT4_NOJOURNAL_MAX_REF_COUNT`.

- `ext4_journal_check_start(struct super_block *sb)`
  - Verifies journal start is allowed.
  - Checks emergency state, read-only superblock, full freeze warning, and aborted journal state.
  - If the journal aborted, calls `ext4_abort()` and returns `-EROFS`.

- `__ext4_journal_start_sb(...)`
  - Tracepoints journal starts by inode or superblock.
  - Calls `ext4_journal_check_start()`.
  - Uses no-journal pseudo-handle when no journal exists or fast commit replay is active.
  - Otherwise starts JBD2 with `jbd2__journal_start()` using `GFP_NOFS`.

- `__ext4_journal_stop(...)`
  - Stops a journal handle.
  - Handles no-journal pseudo-handles separately.
  - Preserves `handle->h_err`, calls `jbd2_journal_stop()`, and reports ext4 standard errors when needed.

- `__ext4_journal_start_reserved(...)`
  - Starts a pre-reserved JBD2 handle after validating the filesystem state.
  - Frees the reserved handle on start failure.

- `__ext4_journal_ensure_credits(...)`
  - Ensures a handle has enough buffer and revoke credits.
  - Returns success for no-journal handles.
  - Fails with `-EROFS` for aborted handles.
  - Extends the transaction when current credits are insufficient.

- `ext4_journal_abort_handle(...)`
  - Records handle error, traces buffer abort, prints transaction abort context, and aborts the JBD2 handle.

- `ext4_check_bdev_write_error(struct super_block *sb)`
  - In no-journal paths, checks block-device writeback errors using `errseq`.
  - Reports async metadata writeback errors through `ext4_error_err()` to avoid reusing stale metadata.

- `__ext4_journal_get_write_access(...)`
  - Gets JBD2 write access for a metadata buffer.
  - In no-journal mode, checks block-device write errors instead.
  - Assigns JBD2 buffer triggers when metadata checksums are enabled and a trigger type is supplied.

- `__ext4_forget(...)`
  - Forgets or revokes freed blocks.
  - No-journal path clears dirty state, waits on the buffer, and calls `__bforget()`.
  - Full data journaling and non-journaled data use `jbd2_journal_forget()`.
  - Metadata or journaled data in ordered/writeback cases uses `jbd2_journal_revoke()`.
  - On revoke failure, aborts the handle and reports an ext4 error.

- `__ext4_journal_get_create_access(...)`
  - Gets create access for newly created metadata buffers and installs checksum triggers when needed.

- `__ext4_handle_dirty_metadata(...)`
  - Marks metadata buffers dirty.
  - In journal mode, uses `jbd2_journal_dirty_metadata()`.
  - In no-journal mode, marks via `mmb_mark_buffer_dirty()` for inode metadata buffers or `mark_buffer_dirty()`.
  - If the inode needs synchronous updates, syncs the dirty buffer and reports I/O errors.

## Error Handling

- Journal access errors generally abort the current handle.
- Metadata dirty failures are treated as severe unless the handle is already aborted.
- Standard ext4 error reporting is used to update filesystem error state.
- No-journal paths still check block-device writeback errors to avoid silent metadata corruption.

## Dependencies

- Includes `ext4_jbd2.h`.
- Uses JBD2 APIs, ext4 error reporting, mount options, ext4 feature checks, buffer-head helpers, tracepoints, and errseq writeback tracking.

## Research Notes

This file is the operational bridge between ext4 metadata mutation and JBD2 transaction semantics. Its no-journal pseudo-handle path is a notable design point: callers can use the same wrapper APIs whether a journal exists or not, but correctness still depends on explicit dirtying, syncing, and block-device write-error checks.
