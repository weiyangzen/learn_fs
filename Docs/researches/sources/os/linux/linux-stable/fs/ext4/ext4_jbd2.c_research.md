# File Research: sources/os/linux/linux-stable/fs/ext4/ext4_jbd2.c

## Summary
Implements ext4's concrete wrapper layer around JBD2. It selects inode data journaling mode, starts and stops journal handles, supports no-journal pseudo-handles, manages reserved handles and credits, revokes or forgets freed blocks, attaches metadata checksum triggers, detects backing-device metadata writeback errors, and dirties metadata buffers.

## Main Responsibilities
- Determines per-inode data mode with `ext4_inode_journal_mode()`.
- Validates journal start conditions against forced shutdown, emergency read-only, read-only superblocks, freeze state, and aborted journals.
- Starts normal, superblock, reserved, and no-journal transactions.
- Stops transactions and reports handle errors through ext4 superblock error paths.
- Ensures transaction and revoke credits are available, extending transactions when needed.
- Aborts handles on JBD2 failures and records the first handle error.
- Implements ext4 forget/revoke policy for metadata blocks and journaled data.
- Gets write/create access to metadata buffers and installs checksum triggers when needed.
- Marks metadata dirty through JBD2 or through buffer dirtying in no-journal mode.

## Key APIs
- `ext4_inode_journal_mode()`.
- `__ext4_journal_start_sb()`.
- `__ext4_journal_stop()`.
- `__ext4_journal_start_reserved()`.
- `__ext4_journal_ensure_credits()`.
- `__ext4_journal_get_write_access()`.
- `__ext4_forget()`.
- `__ext4_journal_get_create_access()`.
- `__ext4_handle_dirty_metadata()`.

## Important Behavior
No-journal operation is represented by small non-pointer `handle_t *` values stored in `current->journal_info`; `ext4_get_nojournal()` and `ext4_put_nojournal()` increment and decrement this pseudo-reference count.

Data journaling is disabled for encrypted regular file data, falling back to ordered mode. Full data journaling also bypasses revoke use in `__ext4_forget()` because the journal does not need those revoke records.

`__ext4_journal_get_write_access()` checks the block device writeback errseq in no-journal mode. This protects against re-reading stale metadata after an asynchronous metadata write failed.

`__ext4_handle_dirty_metadata()` always marks buffers metadata, priority, and uptodate. With a valid journal handle it calls `jbd2_journal_dirty_metadata()`. Without a journal it marks the buffer dirty directly, optionally through the inode's metadata buffer tracker, and synchronously writes it for sync inodes.

## Dependencies
Depends on `ext4_jbd2.h`, JBD2 transaction APIs, ext4 error reporting from `super.c`, tracepoints in `trace/events/ext4.h`, buffer-head state, and metadata checksum feature state from `ext4.h`.

## Risks
Correctness hinges on passing the right handle type: no-journal pseudo-handles must never be treated as real JBD2 handles. Revoke decisions depend on data mode and metadata classification. Credit shortages, aborted journals, and async metadata writeback errors all feed into filesystem shutdown or read-only behavior, so silent handling mistakes can corrupt on-disk state.
