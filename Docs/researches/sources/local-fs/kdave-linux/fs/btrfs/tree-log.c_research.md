# File Research: sources/local-fs/kdave-linux/fs/btrfs/tree-log.c

## Purpose

`tree-log.c` implements Btrfs tree logging: the per-subvolume write-ahead log used to make `fsync()`/`O_SYNC` durable without forcing a full transaction commit. It logs inode items, file extents, directory index ranges, xattrs, inode references, checksums, and enough parent/ancestor metadata to replay post-crash state correctly.

The file covers both sides of the log lifecycle:

- Runtime logging for fsync/link/rename/unlink operations.
- Log commit and superblock update.
- Mount-time log replay.
- Log tree cleanup at transaction commit or recovery.

## Core Concepts

The tree log is a special B-tree per subvolume root, with a top-level log root tree recording each subvolume log root. During recovery, Btrfs replays log trees in stages:

1. `LOG_WALK_PIN_ONLY`: pin log metadata/data extents so replay does not overwrite them.
2. `LOG_WALK_REPLAY_INODES`: recreate inode items, replay xattr deletes, directory delete ranges, and prepare link-count fixups.
3. `LOG_WALK_REPLAY_DIR_INDEX`: replay directory index items.
4. `LOG_WALK_REPLAY_ALL`: replay inode refs/extrefs, xattrs, and file extents.

`struct walk_control` carries replay/free traversal state, including the current log root, target subvolume root, transaction handle, path scratch space, current log leaf/key/slot, and mode flags for pinning/freeing.

## Log Transaction Management

`start_log_trans()` ensures the global log root tree exists, creates a per-root log tree if needed, joins the current log transaction, registers the caller’s `btrfs_log_ctx`, and handles zoned filesystem restrictions. If the log cannot be safely used it returns `BTRFS_LOG_FORCE_COMMIT`.

`join_running_log_trans()` joins an existing log transaction so rename/unlink helpers can update already-running logs. `btrfs_pin_log_trans()` and `btrfs_end_log_trans()` keep log commits from racing with in-progress updates.

`wait_log_commit()` and `wait_for_writer()` coordinate two alternating log transaction slots and wait queues.

## Log Commit

`btrfs_sync_log()` writes a subvolume log root and the log root tree, waits for writeback, updates the superblock log root fields, and wakes all waiters. It carefully serializes against transaction commits with `tree_log_mutex`.

Important behaviors:

- Detects full-commit fallback with `btrfs_need_log_full_commit()`.
- Uses dirty log page marks `EXTENT_DIRTY_LOG1`/`EXTENT_DIRTY_LOG2`.
- Handles zoned filesystem sequential-write constraints.
- Updates the log root tree using `update_log_root()`.
- Writes all supers only after log tree and log root tree writeback succeeds.
- Propagates log commit result to all `btrfs_log_ctx` waiters.

Failure paths mark the transaction/log as needing a full commit and may abort the transaction for serious write/superblock errors.

## Log Replay

`btrfs_recover_log_trees()` is the mount-time entry point. It starts a transaction, pins the log root tree, iterates all logged roots, and replays each root through the staged walk described above. After full replay it runs `fixup_inode_link_counts()`, initializes the root free-objectid state, commits the replay transaction, and clears recovery state.

`walk_log_tree()`, `walk_down_log_tree()`, and `walk_up_log_tree()` traverse log-tree blocks. Depending on `walk_control`, they pin extents, replay leaves, or free log blocks. `process_one_buffer()` handles pinning/free-prep and excludes logged extents for mixed block groups.

`replay_one_buffer()` processes log leaf items by stage:

- Inode stage:
  - Skips zero-link tmpfiles/deleted files.
  - Replays xattr deletes.
  - Replays directory delete ranges for logged directories.
  - Copies inode items with `overwrite_item()`.
  - Drops regular-file extents beyond logged i_size before extent replay.
  - Adds logged inodes to the fixup directory.
- Directory index stage:
  - Replays logged `BTRFS_DIR_INDEX_KEY` entries.
- Full stage:
  - Copies xattrs.
  - Replays inode refs/extrefs.
  - Replays file extents.

`do_abort_log_replay()` provides rich diagnostics on replay failure, dumping current subvolume/log leaves and key/slot context before aborting.

## Item and Extent Replay

`overwrite_item()` copies or resizes an item from the log tree into the subvolume tree. It preserves existing inode `nbytes`, avoids overwriting existing inodes when the logged generation is zero, preserves directory sizes during replay, and fills generation numbers when needed.

`replay_one_extent()` replays inline, regular, prealloc, and explicit-hole extents. It:

- Drops overlapping subvolume extents.
- Inserts or overwrites the logged file extent item.
- Adds or increments extent-tree references.
- Traces qgroups for replayed extents.
- Copies logged checksums into the checksum tree while deleting overlapping checksum ranges first.
- Updates inode file extent ranges, `nbytes`, and inode item.

This function is one of the file’s most correctness-sensitive areas because replayed file extents may reference existing allocated extents, newly logged extents, cloned ranges, compressed extents, or holes.

## Directory Replay and Conflict Resolution

Directory replay is driven by logged directory index items plus `BTRFS_DIR_LOG_INDEX_KEY` range items. Range items mark spans where the log is authoritative: if a directory entry exists in the subvolume tree but not in the log for a logged range, it must be removed during replay.

Key helpers:

- `find_dir_range()` finds authoritative logged ranges.
- `replay_dir_deletes()` scans subvolume directory entries in logged ranges and removes entries missing from the log.
- `check_item_in_log()` checks a subvolume dir index item against the log and unlinks it if needed.
- `replay_one_name()` adds a logged directory entry after deleting conflicting destination name/index entries.
- `replay_one_dir_item()` replays one logged directory index item and schedules link-count fixup for non-directory targets.

Conflict handling is extensive. `drop_one_dir_item()`, `unlink_inode_for_log_replay()`, `__add_inode_ref()`, `unlink_refs_not_in_log()`, and `unlink_extrefs_not_in_log()` remove stale or conflicting references before adding logged names/refs.

## Inode References and Link Counts

`add_inode_ref()` replays `BTRFS_INODE_REF_KEY` and `BTRFS_INODE_EXTREF_KEY` items. It resolves parent dirs, verifies whether the dentry already exists, removes conflicting old refs/names, inserts missing links, updates inode items, unlinks stale refs not present in the log, and finally overwrites the inode ref item.

Because link counts can be wrong after partial replay, the file uses a temporary fixup mechanism:

- `link_to_fixup_dir()` records inodes needing link-count recalculation under `BTRFS_TREE_LOG_FIXUP_OBJECTID`.
- `fixup_inode_link_count()` counts inode refs/extrefs, updates `i_nlink`, resets directory index state, replays recursive directory deletion for zero-link dirs, and inserts orphan items.
- `fixup_inode_link_counts()` drains all fixup entries after replay.

This design avoids complex incremental link-count correctness during every replay subcase.

## Xattr Replay

`btrfs_log_all_xattrs()` logs all xattrs for an inode. This is deliberate: during replay, `replay_xattr_deletes()` deletes xattrs present in the subvolume tree but missing from the log, giving fsync semantics consistent with journaling filesystems.

## Runtime Logging

`btrfs_log_inode()` is the central logging routine. It supports:

- `LOG_INODE_ALL`: full inode logging.
- `LOG_INODE_EXISTS`: enough metadata to recreate/keep the inode reachable.
- Directory full logging with directory range items.
- Fast fsync for changed extents.
- Full sync fallback when safe logging is impossible.

Major responsibilities:

- Determine whether inode was logged before with `inode_logged()`.
- Drop or truncate stale log items before relogging.
- Copy inode metadata, refs, extents, and xattrs.
- Log holes for `NO_HOLES`.
- Log prealloc extents beyond EOF.
- Log changed extent maps and checksums.
- Log delayed directory insertions/deletions.
- Discover and log conflicting inodes.
- Update `logged_trans`, `last_log_commit`, and reflink tracking.

`copy_inode_items_to_log()` scans subvolume items changed in the current transaction and batches them into the log. It detects name conflicts against the commit root using `btrfs_check_ref_name_override()` and queues conflicting inodes.

`copy_items()` clones the source leaf before copying to the log to avoid lock dependency deadlocks. It filters old extents when safe, logs checksums for new regular extents, and fills inode items from live in-memory inode state.

`log_one_extent()`, `btrfs_log_changed_extents()`, `log_extent_csums()`, and `log_csums()` implement fast fsync extent and checksum logging. They handle ordered extents, reflink checksum overlap hazards, compression, prealloc extents, and modified extent-map ordering.

## Directory Logging

`log_directory_changes()` and `log_dir_items()` log directory index items changed in the current transaction and insert range items for gaps/deletions. `process_dir_items_leaf()` clones source leaves, batches dir index copies, and marks `ctx->log_new_dentries` when newly logged dentries require logging their target inodes.

Delayed directory items are handled separately:

- `btrfs_log_get_delayed_items()` is used by callers here to collect delayed insert/delete lists.
- `log_delayed_insertion_items()` logs delayed dir index insertions in batches.
- `log_delayed_deletion_items()` logs deletions either as full directory ranges or incremental removals/ranges.
- `log_new_delayed_dentries()` logs inode targets referenced by delayed insertions.

`log_new_dir_dentries()` recursively logs newly created dentries under a directory, limiting recursion and avoiding VFS inode locks to prevent lockdep cycles.

## Parent and Ancestor Logging

`btrfs_log_inode_parent()` wraps inode logging with parent/ancestor safety. It forces transaction commit when tree logging is disabled, the root is deleted, or the subvolume was created in the current transaction.

It also:

- Logs all parents after unlink-sensitive operations via `btrfs_log_all_parents()`.
- Logs newly created ancestors via `log_all_new_ancestors()`.
- Logs new dentries if directory logging discovered them.

`log_new_ancestors_fast()` walks the dentry chain for simple single-link cases. `log_new_ancestors()` and `log_all_new_ancestors()` use inode ref items for hard-link cases, falling back on complex extref cases.

`btrfs_log_dentry_safe()` is the exported fsync-facing entry point around `btrfs_log_inode_parent()`.

## Rename/Unlink/Subvolume Hooks

The file exports hooks used by other Btrfs operations to keep the log safe:

- `btrfs_del_dir_entries_in_log()` removes logged directory entries after unlink/rename.
- `btrfs_del_inode_ref_in_log()` removes logged inode refs after unlink/rename.
- `btrfs_record_unlink_dir()` records unlink/rename transaction IDs to force safe parent logging or full commits.
- `btrfs_record_snapshot_destroy()` makes parent directory fsync force a full commit after snapshot deletion.
- `btrfs_record_new_subvolume()` prevents logging parent directories with entries pointing to unpersisted roots.
- `btrfs_log_new_name()` updates the log after link/rename by deleting the old logged dentry if needed and logging the inode’s new name/parents in `LOG_INODE_EXISTS` mode.

These functions are central to preventing stale names, duplicate links, lost directories, and replay of invalid subvolume entries.

## Log Cleanup

`free_log_tree()` walks a log tree with `free = true`, cleans log buffers, releases dirty log page and checksum range state, and drops the root. If traversal fails, it marks `BTRFS_FS_STATE_LOG_CLEANUP_ERROR`, flushes remaining dirty log pages, and aborts/handles the filesystem error.

`btrfs_free_log()` frees a subvolume log root. `btrfs_free_log_root_tree()` frees the global log root tree.

## Error Handling and Fallback Strategy

The file uses three broad failure strategies:

- Return normal negative errors for allocation/search/copy failures.
- Return `BTRFS_LOG_FORCE_COMMIT` when tree logging is unsafe but a full transaction commit can preserve correctness.
- Abort the transaction on replay or writeback failures that indicate filesystem/log corruption or unrecoverable I/O failure.

Many paths mark the transaction with `btrfs_set_log_full_commit()` so future fsync attempts fall back to a full commit.

## Important Invariants

- Log replay must not overwrite log-tree extents before replay is complete, hence pinning.
- Directory replay relies on logging only dir index keys plus authoritative range items.
- Logged inode item generation zero means “inode exists” and must not overwrite full existing inode metadata.
- Xattrs are logged as a complete set so missing logged xattrs imply deletion.
- Link counts are repaired after replay rather than maintained perfectly during all intermediate steps.
- Source leaves are cloned before log mutation to avoid subvolume/log tree lock inversions.
- Rename/link/unlink operations must update or invalidate existing log state before a log commit can race in.
- Complex cases involving new subvolumes, deleted snapshots, unsafe directory renames, or too many conflicts force full transaction commit.

## External Dependencies

The implementation is tightly coupled to Btrfs internals:

- B-tree search/insert/delete: `btrfs_search_slot()`, `btrfs_insert_empty_item(s)()`, `btrfs_del_item(s)()`.
- Extent handling: `btrfs_drop_extents()`, `btrfs_alloc_logged_file_extent()`, delayed refs, qgroups.
- Checksums: `btrfs_lookup_csums_list()`, `btrfs_insert_data_csums()`, `btrfs_del_csums()`.
- Directory/inode helpers: `btrfs_add_link()`, `btrfs_unlink_inode()`, inode refs/extrefs, delayed inode items.
- Transaction and root management: log root tree, root items, superblock writes.
- VFS/fscrypt: dentries, inodes, names, encrypted filename setup.

## Research Notes

This file is the main correctness hub for Btrfs fsync semantics. Most complexity comes from making partial metadata persistence equivalent to a full transaction commit after crash replay, especially across rename/link/unlink, directory fsync, delayed dir items, reflinked extents, xattr deletion, and subvolume/snapshot operations.
