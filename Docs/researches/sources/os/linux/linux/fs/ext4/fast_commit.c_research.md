# File Research: sources/os/linux/linux/fs/ext4/fast_commit.c

Implements ext4 fast commits: fine-grained TLV journaling for selected inode, dentry, and data-range updates, plus recovery scan/replay logic.

Key behavior:
- Tracks fast-commit eligibility with `ext4_fc_disabled()`, `ext4_fc_eligible()`, and `ext4_fc_mark_ineligible()`.
- Tracks per-inode fast-commit state through `i_sync_tid`, `i_fc_list`, `i_fc_lblk_start`, and `i_fc_lblk_len`.
- Tracks dentry operations for create/link/unlink via `ext4_fc_track_create()`, `ext4_fc_track_link()`, and `ext4_fc_track_unlink()`.
- Marks encrypted filenames, inline data, journal-data mode, xattrs, unsupported operations, and allocation failures as fast-commit ineligible.
- `ext4_fc_track_inode()` waits for an inode already being fast-committed before enqueueing a new update.
- `ext4_fc_track_range()` coalesces modified logical block ranges for later ADD_RANGE / DEL_RANGE emission.
- Commit serialization writes TLVs for:
  - `HEAD`
  - dentry create/link/unlink updates
  - data range adds/deletes
  - raw inode snapshots
  - `TAIL` with transaction id and CRC
- `ext4_fc_reserve_space()` manages fast-commit block packing and emits `PAD` TLVs when records do not fit in the current block.
- `ext4_fc_write_tail()` ends each fast commit on a block boundary and uses barriers/FUA when mounted with barriers.
- `ext4_fc_perform_commit()` flushes inode data, locks journal updates to mark committing inodes, writes TLVs, and submits the tail.
- `ext4_fc_commit()` coordinates with JBD2 fast-commit begin/end APIs, raises I/O priority to journal priority during the commit, updates stats, and falls back to a full commit when needed.
- `ext4_fc_cleanup()` clears committing state, wakes waiters, releases dentry update records, moves staging queues to main queues, and clears ineligibility after the relevant tid.
- Replay scan validates TLV lengths, CRCs, tail tids, and supported features, and records physical regions needed by ADD_RANGE tags.
- Replay handlers enforce idempotent outcomes for unlink, link, create, inode snapshot, add range, and delete range.
- Replay records modified inodes and later reconstructs block bitmap state by walking their extents.
- Exposes fast-commit stats and ineligibility reasons through `ext4_fc_info_show()`.
- Creates/destroys the slab cache for `struct ext4_fc_dentry_update`.

Important interactions:
- Fast commit is built around JBD2 fast-commit callbacks and queues in `struct ext4_sb_info`.
- Uses `s_fc_lock` for global fast-commit queues and `i_fc_lock` for per-inode fast-commit state.
- Uses `EXT4_STATE_FC_FLUSHING_DATA` and `EXT4_STATE_FC_COMMITTING` to coordinate evict, track, and commit paths.
- Replay depends on extent helpers, bitmap marking, inode checksum reset, and regular ext4 namei helpers.
