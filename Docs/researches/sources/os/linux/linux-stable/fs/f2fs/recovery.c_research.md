# File Research: sources/os/linux/linux-stable/fs/f2fs/recovery.c

## Purpose

`recovery.c` implements F2FS roll-forward recovery for fsynced data after an unclean shutdown. It scans the warm node chain after the last checkpoint, identifies fsynced dnodes, reconstructs missing inode/dentry state when needed, replays inode and data block updates, and writes a checkpoint after successful recovery.

## Recovery Model

The opening comment documents recovery scenarios involving:

- `F`: fsync mark.
- `D`: dentry mark.
- inode nodes before/after checkpoint.
- dnodes after checkpoint.

The recovery logic handles cases where inode updates and fsynced dnodes appear in different orders around checkpoint, including missing dentry/inode node recovery and dropping unrecoverable dnodes.

## Roll-Forward Capacity

- `f2fs_space_for_roll_forward()`
  - Checks that current valid blocks plus newly allocated blocks do not exceed user block count.
  - Enforces optional `max_rf_node_blocks` limit through `rf_node_block_count`.

## Fsync Inode List Management

- `get_fsync_inode()`
  - Finds an inode entry in a recovery list by inode number.

- `add_fsync_inode()`
  - Loads inode with retry.
  - Initializes quota.
  - Optionally allocates quota inode usage for recovered newly-created inode pages.
  - Allocates and appends an `fsync_inode_entry`.

- `del_fsync_inode()` / `destroy_fsync_dnodes()`
  - Drop inode references and free recovery list entries.
  - Optionally call `f2fs_inode_synced()` to drop unrecovered inode state.

## Filename and Dentry Recovery

- `init_recovered_filename()`
  - Builds an `f2fs_filename` from raw inode name and name length.
  - Handles unencrypted names directly.
  - For encrypted+casefolded directories, reads the saved hash from the raw name area.
  - For casefolded directories with keys, computes casefolded hash.
  - Rejects excessive name length and invalid encrypted hash layout.

- `recover_dentry()`
  - Ensures the parent directory inode is available in `dir_list`.
  - Looks for the recovered filename in the parent.
  - If an entry exists for another inode, loads that inode, initializes quota, acquires orphan capacity, deletes the stale entry, and retries.
  - If absent, adds a recovered dentry for the inode.
  - Retries on `-ENOMEM`.
  - Logs recovered name as `"<encrypted>"` when appropriate.

## Inode Metadata Recovery

- `recover_quota_data()`
  - Compares raw recovered uid/gid with current inode ownership.
  - Uses `dquot_transfer()` to update quota accounting when ownership changed.
  - Marks `SBI_QUOTA_NEED_REPAIR` on transfer error.

- `recover_inline_flags()`
  - Restores `FI_PIN_FILE` and `FI_DATA_EXIST` from raw inline flags.

- `recover_inode()`
  - Restores mode, uid/gid, project quota, size, atime/ctime/mtime, advise, flags, inode flags, GC failures, and inline state.
  - Transfers project quota if needed.
  - Calls `f2fs_set_inode_flags()` and marks inode dirty sync.
  - Logs recovered inode details.

## Node Chain Discovery

- `adjust_por_ra_blocks()`
  - Dynamically adjusts recovery readahead window.
  - Doubles readahead on sequential next-block chains, halves toward minimum on non-segment-boundary discontinuity.

- `sanity_check_node_chain()`
  - Uses Floyd cycle detection against the roll-forward node chain.
  - Reads fast-pointer nodes, validates recoverability, advances by two links, and readaheads.
  - Returns `-EINVAL` if a loop is detected.

- `find_fsync_dnodes()`
  - Starts from `NEXT_FREE_BLKADDR()` of `CURSEG_WARM_NODE`.
  - Walks node chain while block addresses are valid and nodes are recoverable.
  - Tracks fsync-marked dnodes.
  - If a fsynced inode+dentry node is found and recovery is not check-only, calls `f2fs_recover_inode_page()` for missing new inode pages.
  - Adds fsynced inode entries.
  - Records latest fsync block and latest dentry block per inode entry.
  - In check-only mode, reports existence of recoverable new inode state through `new_inode`.

## Previous Ownership Checks

- `check_index_in_prev_nodes()`
  - Determines whether the destination data block being replayed is still referenced by a previous node.
  - Reads segment summary from current curseg summary or summary page.
  - Validates summary offset against max addresses in node.
  - If the previous reference belongs to the same inode or node, truncates that data block reference directly.
  - Otherwise loads the referenced inode and dnode, and truncates the previous data block if it still points at the replay destination.
  - Temporarily unlocks/relocks inode folio when needed to avoid lock conflicts.
  - Reports inconsistent summaries as corruption.

## Data Recovery

- `f2fs_reserve_new_block_retry()`
  - Retries `f2fs_reserve_new_block()` up to `DEFAULT_FAILURE_RETRY_COUNT`.

- `do_recover_data()`
  - Replays one recoverable node folio for an inode.
  - Step 1: recover inline xattr or external xattr node.
  - Step 2: recover inline data.
  - Step 3: replay data block address indices.
  - Locates/allocates corresponding current dnode with `f2fs_get_dnode_of_data(..., ALLOC_NODE)`.
  - Validates current and recovered block addresses under `META_POR`.
  - Handles cases:
    - same source/destination: skip
    - recovered destination `NULL_ADDR`: truncate current source
    - recovered destination `NEW_ADDR`: truncate current source and reserve a new block
    - recovered destination valid: reserve if current source is null, remove stale previous references, validate destination is not currently valid data, and replace block mapping
  - Grows inode size unless `file_keep_isize()` is set.
  - Copies recovered node footer into current node folio and marks it dirty.
  - Logs recovered range and count.

- `recover_data()`
  - Walks the same warm node chain and replays only nodes belonging to discovered fsynced inodes.
  - Recovers inode metadata when the folio is an inode node.
  - Recovers dentry when the entry’s last dentry block matches the current block.
  - Calls `do_recover_data()` for each relevant dnode.
  - Moves completed inode entries to a temporary list once their last fsync block is replayed.
  - Allocates new segments after successful replay.
  - Logs recoverable/fsynced/total dnode counts and recovered inode/dentry/dnode counts.

## Top-Level Recovery

- `f2fs_recover_fsync_data()`
  - Logs check-only or real recovery mode.
  - Takes `cp_global_sem` write lock to prevent checkpoint during recovery.
  - Step 1: calls `find_fsync_dnodes()`.
  - In check-only mode, returns `1` when fsync data or new inode recovery is needed.
  - Step 2: calls `recover_data()` for real recovery.
  - Destroys inode recovery lists, truncates recovery meta pages, and on error truncates node/meta mappings fully.
  - Checks and fixes zoned-device write pointer consistency after successful recovery.
  - Clears `SBI_POR_DOING` on success.
  - Drops directory inode list after releasing checkpoint lock.
  - If recovery ran, sets `SBI_IS_RECOVERED` and writes a checkpoint with reason `CP_RECOVERY`.
  - Restores original superblock flags, including readonly status.

## Cache Lifecycle

- `f2fs_create_recovery_cache()`
  - Creates `f2fs_fsync_inode_entry` slab cache.

- `f2fs_destroy_recovery_cache()`
  - Destroys the recovery entry slab cache.

## Interactions

- Uses `node.h` helpers for fsync/dentry marks, node footer checkpoint version, and next block chain.
- Calls `node.c` recovery helpers:
  - `f2fs_recover_inode_page()`
  - `f2fs_recover_inline_xattr()`
  - `f2fs_recover_xattr_data()`
  - `f2fs_get_dnode_of_data()`
- Uses directory helpers to find/delete/add entries.
- Uses segment summaries and block replacement to avoid duplicate data block ownership.
- Invoked from mount/superblock recovery flow in `super.c`.

## Consistency and Error Handling

- Detects looped node chains and aborts with a notice.
- Validates recovered block addresses before use.
- Converts inconsistent summaries and invalid metadata into `-EFSCORRUPTED` or error flags.
- Uses retry loops for memory allocation pressure and block reservation.
- On recovery failure, keeps filesystem from silently proceeding with stale recovery pages by truncating node/meta mappings.
