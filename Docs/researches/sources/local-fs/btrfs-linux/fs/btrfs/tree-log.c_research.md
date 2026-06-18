# File Research: sources/local-fs/btrfs-linux/fs/btrfs/tree-log.c

## Purpose

`tree-log.c` implements Btrfs tree logging: a specialized write-ahead log used to satisfy `fsync()`/`O_SYNC` without committing the full filesystem transaction. Instead of forcing a full tree commit for every sync, changed inode, extent, directory, xattr, checksum, and reference items are copied into per-subvolume log trees. After a crash, mount-time log replay copies those items back into the subvolume trees, restores extent/checksum references, replays directory deletions, repairs link counts, and then frees the log.

The file covers both sides of the mechanism:
- Runtime logging and log commit for fsync paths.
- Mount-time log recovery and replay.
- Directory rename/link/unlink consistency tracking.
- Log tree lifetime, writeout, cleanup, and full-commit fallback decisions.

## Major Concepts

The log tree is replayed in staged passes:
- `LOG_WALK_PIN_ONLY`: pin log metadata and logged extents so replay does not overwrite them.
- `LOG_WALK_REPLAY_INODES`: recreate/copy inode items, replay xattr deletes, and prepare directory deletes.
- `LOG_WALK_REPLAY_DIR_INDEX`: replay logged directory index entries.
- `LOG_WALK_REPLAY_ALL`: replay inode references, xattrs, file extents, checksums, and final fixups.

`struct walk_control` carries replay state: target root, log root, transaction, replay stage, currently processed log leaf/key/slot, and a scratch subvolume path. The custom `btrfs_abort_log_replay()` wrapper records detailed replay diagnostics, including both the current subvolume leaf and log leaf.

## Logging Transaction Flow

`start_log_trans()` creates or joins a per-root log tree, handles the global log-root tree, increments log writer counts, and attaches `btrfs_log_ctx` objects to the active log transaction. It has special handling for zoned filesystems because sequential write constraints can force a full transaction commit.

`join_running_log_trans()`, `btrfs_pin_log_trans()`, and `btrfs_end_log_trans()` coordinate log writers and operations such as rename/link updates that must keep the log from being committed while multiple related updates are applied.

`btrfs_sync_log()` is the main log commit path. It:
- Serializes per-root log commits with two alternating commit slots.
- Waits for active log writers.
- Writes marked dirty log extents.
- Updates the tree of log roots.
- Writes the log-root tree.
- Updates superblocks with the log root bytenr/level.
- Wakes waiters and records commit completion.
Failures, ENOSPC, writeback problems, zoned-write conflicts, or consistency risks mark the transaction for full commit through `btrfs_set_log_full_commit()`.

## Log Replay

`btrfs_recover_log_trees()` is the mount-time recovery entrypoint. It starts a transaction, pins the log-root tree, iterates each per-subvolume log tree, and replays it through the staged walk sequence. After `LOG_WALK_REPLAY_ALL`, it fixes link counts and refreshes the root free objectid cache before committing the replay transaction.

The replay walker is built from:
- `walk_log_tree()`
- `walk_down_log_tree()`
- `walk_up_log_tree()`
- `process_one_buffer()`
- `replay_one_buffer()`

`replay_one_buffer()` dispatches by key type and stage. It handles inode items, directory index items, xattrs, inode refs/extrefs, and extent data. It deliberately ignores legacy `BTRFS_DIR_ITEM_KEY` log entries because modern logging derives them from directory index items.

## Item and Extent Replay

`overwrite_item()` copies a log item into the subvolume tree, inserting, resizing, or replacing the destination item. It preserves important inode semantics: generation zero means “inode exists” logging, directory size is protected during replay, and inode generation is filled in when needed.

`replay_one_extent()` replays inline, regular, preallocated, and explicit-hole file extent items. It drops overlapping extents, inserts the logged file extent, restores extent references in the extent tree, traces qgroup ownership, replays checksums from the log, deletes overlapping csum ranges first, updates inode extent ranges, and fixes inode byte counts.

Checksum handling is careful around cloned/reflinked extents:
- `log_csums()` serializes overlapping log checksum ranges with `log_csum_range`.
- Replay deletes existing csum ranges before inserting logged sums to avoid overlapping checksum items.

## Directory and Reference Replay

Directory replay combines positive entry replay with authoritative deletion ranges:
- `insert_dir_log_key()` records ranges of directory index offsets where the log is authoritative.
- `replay_dir_deletes()` scans subvolume directory entries in those ranges and removes entries absent from the log.
- `check_item_in_log()` performs per-entry deletion checks.
- `replay_one_name()` and `replay_one_dir_item()` restore directory entries while resolving conflicts.

Reference replay handles old-style refs and extended refs:
- `add_inode_ref()`
- `__add_inode_ref()`
- `unlink_refs_not_in_log()`
- `unlink_extrefs_not_in_log()`
- `unlink_old_inode_refs()`

These routines prevent stale names, conflicting sequence numbers, and inconsistent dir-index/name/backref combinations. Conflicting entries are unlinked through normal Btrfs helpers and queued for link-count fixup.

## Link Count Fixups

Some replay paths intentionally defer exact link-count correctness. The file uses a synthetic fixup namespace:
- `link_to_fixup_dir()` inserts fixup records under `BTRFS_TREE_LOG_FIXUP_OBJECTID`.
- `fixup_inode_link_counts()` scans those records after replay.
- `fixup_inode_link_count()` counts inode refs/extrefs, updates `i_nlink`, resets directory index counters, and inserts orphan items for zero-link inodes.

This is central to safely replaying partial directory fsyncs, hard links, renamed files, and directory deletions.

## Runtime Inode Logging

`btrfs_log_inode()` is the core inode logging routine. It supports:
- `LOG_INODE_ALL`: full inode and data metadata logging.
- `LOG_INODE_EXISTS`: minimal logging to prove an inode exists for replay.
- Directory-specific logging of index ranges and delayed items.
- Fast fsync logging of modified extent maps.
- Full-sync fallback when correctness cannot be guaranteed.

It coordinates:
- inode item creation via `log_inode_item()` and `fill_inode_item()`
- copying changed items with `copy_inode_items_to_log()`
- copying xattrs through `btrfs_log_all_xattrs()`
- logging holes for `NO_HOLES` filesystems via `btrfs_log_holes()`
- logging changed extents through `btrfs_log_changed_extents()`
- logging prealloc extents beyond EOF through `btrfs_log_prealloc_extents()`

The implementation distinguishes “fast search” extent logging from full item-copy logging and uses `ctx->scratch_eb` clones to avoid lock ordering problems between subvolume leaves, log tree updates, delayed nodes, and metadata allocation.

## Directory Logging and Delayed Items

Directory logging is range based. `log_directory_changes()` and `log_dir_items()` copy changed `BTRFS_DIR_INDEX_KEY` items and add range keys for gaps/deletions. `process_dir_items_leaf()` and `flush_dir_items_batch()` batch directory item insertion into the log.

Delayed directory index insertions/deletions are handled separately:
- `log_delayed_insertion_items()`
- `log_delayed_deletion_items()`
- `log_delayed_deletions_full()`
- `log_delayed_deletions_incremental()`
- `log_new_delayed_dentries()`

This prevents missing entries that exist only as delayed items or get flushed concurrently while a directory is being logged.

## Rename, Link, Unlink, and Conflict Handling

The file contains extensive logic for rename/link/unlink corner cases:
- `btrfs_record_unlink_dir()` records unlink/rename transaction ids on affected inodes/directories.
- `btrfs_record_snapshot_destroy()` and `btrfs_record_new_subvolume()` force safe full-commit behavior for snapshot/subvolume cases.
- `btrfs_log_new_name()` updates the log after link/rename, deletes old logged dentries when needed, pins the log while updating related state, and logs the new parent chain.
- `btrfs_del_dir_entries_in_log()` and `btrfs_del_inode_ref_in_log()` remove stale names/refs from an already logged inode or directory.

Conflict detection prevents replay from losing older inodes whose names are reused in the current transaction:
- `btrfs_check_ref_name_override()` detects name collisions against the committed root.
- `add_conflicting_inode()` queues conflicting inodes or parents.
- `log_conflicting_inodes()` logs queued conflicts in bounded recursion.
- `MAX_CONFLICT_INODES` limits work; exceeding it forces full commit.

## Parent and Ancestor Logging

`btrfs_log_inode_parent()` wraps inode logging with parent/ancestor safety. It refuses tree logging when `notreelog` is active, the root has no refs, the root was created in the current transaction, or directory/unlink histories require a full commit.

Parent helpers include:
- `btrfs_log_all_parents()` for old/current parents after unlink.
- `log_all_new_ancestors()` for new ancestor chains.
- `log_new_ancestors_fast()` for single-link fast path.
- `log_new_dir_dentries()` for recursively logging newly created dentries.

## Cleanup and Lifetime

`free_log_tree()`, `btrfs_free_log()`, and `btrfs_free_log_root_tree()` free per-root and global log trees at full transaction commit or cleanup time. `clean_log_buffer()` clears dirty state and releases/pins reserved metadata depending on whether a transaction is active. Cleanup errors set `BTRFS_FS_STATE_LOG_CLEANUP_ERROR` and may abort the transaction or report filesystem errors.

## Correctness and Concurrency Themes

The file is dominated by crash-consistency and concurrency constraints:
- Uses log mutexes, inode log mutexes, writer counts, waitqueues, and two-slot commit state.
- Avoids GFP recursion deadlocks with `btrfs_iget_logging()` using `memalloc_nofs_save()`.
- Clones leaves before modifying log trees while reading subvolume leaves.
- Falls back to full transaction commits when partial logging cannot represent a safe replay.
- Handles transient in-memory `logged_trans` state with log-tree searches after inode eviction.
- Treats zoned filesystems specially because log write ordering can otherwise violate sequential-write rules.

## Public API Implemented Here

This file implements the public functions declared in `tree-log.h`, including:
- `btrfs_init_log_ctx()`
- `btrfs_init_log_ctx_scratch_eb()`
- `btrfs_release_log_ctx_extents()`
- `btrfs_sync_log()`
- `btrfs_free_log()`
- `btrfs_free_log_root_tree()`
- `btrfs_recover_log_trees()`
- `btrfs_log_dentry_safe()`
- `btrfs_del_dir_entries_in_log()`
- `btrfs_del_inode_ref_in_log()`
- `btrfs_end_log_trans()`
- `btrfs_pin_log_trans()`
- `btrfs_record_unlink_dir()`
- `btrfs_record_snapshot_destroy()`
- `btrfs_record_new_subvolume()`
- `btrfs_log_new_name()`

## Research Notes

This is a high-risk, correctness-critical implementation file. Most code exists to preserve filesystem semantics after crash replay when only a subset of metadata was fsynced. The safest mental model is that tree logging is not just “copy changed items to a log”; it is a constrained replay language for representing inode existence, file data extents, directory entry presence/absence, reference changes, xattr deletion, checksum restoration, and link-count repair without committing the whole transaction.
