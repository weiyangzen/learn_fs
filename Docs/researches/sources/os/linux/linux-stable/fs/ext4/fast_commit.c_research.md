# File Research: sources/os/linux/linux-stable/fs/ext4/fast_commit.c

This file implements ext4 fast commit tracking, commit emission, cleanup, replay scanning, and replay application. Fast commits store fine-grained filesystem deltas in journal fast-commit space as TLV records and fall back to a full JBD2 commit when an operation is unsupported.

Major responsibilities:
- Track fast-commit-eligible operations:
  - Directory updates via `ext4_fc_track_create()`, `ext4_fc_track_link()`, and `ext4_fc_track_unlink()`.
  - Inode metadata updates via `ext4_fc_track_inode()`.
  - Logical data range changes via `ext4_fc_track_range()`.
- Maintain fast commit queues:
  - `s_fc_q[FC_Q_MAIN/STAGING]` for inodes.
  - `s_fc_dentry_q[FC_Q_MAIN/STAGING]` for directory entry operations.
  - Per-inode `i_fc_list`, `i_fc_dilist`, `i_fc_lblk_start`, and `i_fc_lblk_len`.
- Mark unsupported transactions ineligible with `ext4_fc_mark_ineligible()`, recording the latest ineligible TID and per-reason stats.
- Emit fast commit blocks:
  - `ext4_fc_reserve_space()` allocates TLV space, inserts padding, advances `s_fc_bytes`, and gets fast-commit buffers from JBD2.
  - `ext4_fc_add_tlv()` and `ext4_fc_add_dentry_tlv()` serialize records.
  - `ext4_fc_write_inode()` serializes raw inode state.
  - `ext4_fc_write_inode_data()` serializes added or deleted logical ranges.
  - `ext4_fc_write_tail()` terminates a commit with TID and CRC.
- Execute the commit pipeline:
  - `ext4_fc_commit()` is the main entry point.
  - `ext4_fc_perform_commit()` flushes data, marks inodes committing, writes HEAD/dentry/range/inode/TAIL tags, and submits buffers.
  - `ext4_fc_cleanup()` releases buffers, clears committing state, frees dentry-update records, splices staging queues, clears ineligibility after full commit, and resets fast-commit byte usage after full commits.
- Replay fast commit records during journal recovery:
  - `ext4_fc_replay_scan()` validates TLVs, checks lengths, validates CRC/tail TID, counts replayable tags, and records physical regions that must be excluded from replay allocation.
  - `ext4_fc_replay()` dispatches replay by tag.
  - Replay handlers cover unlink, link, create, raw inode restoration, add-range, and delete-range.
  - `ext4_fc_set_bitmaps_and_counters()` fixes allocation bitmaps for replay-modified inodes.
  - `ext4_fc_replay_cleanup()` releases replay arrays and clears replay mount state.
- Export support hooks:
  - `ext4_fc_init_inode()`, `ext4_fc_del()`, `ext4_fc_init()`, `ext4_fc_info_show()`, `ext4_fc_record_regions()`, `ext4_fc_replay_check_excluded()`, slab init/destroy helpers.

Important design points:
- Fast commits encode outcomes, not procedures, to make replay idempotent. Rename-like sequences are represented as link/unlink/inode-state outcomes.
- A commit is atomic only if a valid tail record with matching TID and CRC is found.
- HEAD is written only at the beginning of a fast-commit area for a transaction.
- TAIL consumes the rest of its block so the next fast commit starts on a fresh block.
- Dentry create records are special: the inode and inode data are written before the create dentry TLV so replay can instantiate the inode then link it.
- Encrypted filenames, journal-data inodes, inline-data range changes, xattr-like cases, and other unsupported cases force full commits through ineligibility.
- The code uses `s_fc_lock` for global queues and `i_fc_lock` for per-inode fast-commit fields. If both are needed, global lock comes first.
- `EXT4_STATE_FC_FLUSHING_DATA` prevents inodes from being evicted while commit-time data flush is in progress.
- `EXT4_STATE_FC_COMMITTING` makes modifiers wait until the inode’s fast commit completes.
- Replay uses arrays of modified inodes and reserved allocation regions because normal allocation decisions during replay may differ from pre-crash allocation.

Key invariants:
- Fast commit tracking is skipped when fast commit is disabled or replay is active.
- Full commit clears the fast-commit area state; fast commit cleanup only consumes committed queue entries.
- `ext4_fc_track_inode()` must not sleep while holding `i_data_sem`.
- TLV lengths are validated before replay dispatch.
- Replay add-range/delete-range must update block allocation accounting and later reconcile bitmaps from modified inode mappings.
- Fast commit recovery intentionally ignores some missing inodes/directories as already-applied or obsolete state, preserving replay idempotence.
