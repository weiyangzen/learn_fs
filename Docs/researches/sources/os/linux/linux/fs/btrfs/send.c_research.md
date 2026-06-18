# File Research: sources/os/linux/linux/fs/btrfs/send.c

## Purpose

`send.c` implements the kernel-side Btrfs send ioctl. It serializes a read-only subvolume, optionally relative to a parent snapshot, into the Btrfs send stream consumed by `btrfs receive`.

The file covers both full sends and incremental sends. It walks Btrfs commit roots, detects new/deleted/changed metadata and file extents, emits send stream commands, and handles difficult receiver-state ordering problems such as renamed directories, orphaned paths, hard links, holes, clones, compressed extents, xattrs, capabilities, and fs-verity.

## Main Entry Point

`btrfs_ioctl_send(struct btrfs_root *send_root, const struct btrfs_ioctl_send_args *arg)` is the public entry point.

It:

- Requires `CAP_SYS_ADMIN`.
- Requires the send root, parent root, and clone roots to be read-only and not dead.
- Rejects roots with dedupe in progress.
- Tracks `send_in_progress` on all participating roots.
- Validates flags, protocol version, clone-source count, and writable output fd.
- Allocates `send_ctx`, send buffers, clone root arrays, and caches.
- Adds the send root itself as an allowed clone source.
- Flushes delalloc and ensures commit roots are up to date.
- Calls `send_subvol()`.
- Emits trailing cached directory utimes and optional `BTRFS_SEND_C_END`.
- Cleans all pending move/orphan trees, root refs, buffers, caches, current inode refs, and file handles on exit.

## Core State

The central structure is `struct send_ctx`.

Important fields:

- Output stream state: `send_filp`, `send_off`, `send_buf`, `send_size`, `send_max_size`, `send_buf_pages`, `put_data`.
- Protocol and flags: `proto`, `flags`.
- Roots: `send_root`, `parent_root`, `clone_roots`, `clone_roots_cnt`.
- Tree comparison state: `left_path`, `right_path`, `cmp_key`.
- Relocation tracking: `last_reloc_trans`, `backref_cache_last_reloc_trans`.
- Current inode state: `cur_ino`, generation, size, mode, rdev, deletion/new-generation flags, write offsets, verity flag, cached path.
- Recorded references: `new_refs`, `deleted_refs`, plus rbtrees for fast matching.
- Rename/move ordering state: `pending_dir_moves`, `waiting_dir_moves`, `orphan_dirs`.
- Caches: inode name cache, backref cache, created-directory cache, delayed directory-utimes cache.
- File data state: current inode pointer, readahead state, page-cache cleanup tracking.

This state is effectively the send stream's model of what the receiver filesystem should look like at the current point in the stream.

## Path Handling

`struct fs_path` is a compact dynamic path builder with a 256-byte inline buffer. It supports normal append and reversed prepend-style construction.

Key helpers:

- `fs_path_alloc()`, `fs_path_alloc_reversed()`, `fs_path_free()`.
- `fs_path_ensure_buf()` grows buffers up to `PATH_MAX`.
- `fs_path_add()`, `fs_path_add_path()`, `fs_path_add_from_extent_buffer()`.
- `fs_path_unreverse()` normalizes reversed paths.
- `get_cur_path()` computes the path an inode should have on the receiver at the current `send_progress`.

`get_cur_path()` is one of the most important functions. It walks inode refs up toward the subvolume root while considering whether ancestors have already been processed, are still waiting for moves, were orphanized, or are pending deletion. For unresolved or conflicting names it generates temporary orphan names with `gen_unique_name()`.

## Send Stream Encoding

The file emits Btrfs send commands as command headers followed by TLV attributes.

Important helpers:

- `send_header()` writes the `btrfs-stream` header.
- `begin_cmd()` starts a command.
- `tlv_put()` and typed wrappers serialize attributes.
- `put_data_header()` handles `BTRFS_SEND_A_DATA`; for protocol v2+ the data attribute length is implicit and must be last.
- `send_cmd()` fills length and CRC32C, writes the command, then resets command buffer state.

Command helpers include:

- `send_rename()`
- `send_link()`
- `send_unlink()`
- `send_rmdir()`
- `send_truncate()`
- `send_chmod()`
- `send_chown()`
- `send_fileattr()`
- `send_utimes()`
- `send_create_inode()`
- `send_set_xattr()`
- `send_remove_xattr()`
- `send_write()`
- `send_clone()`
- `send_update_extent()`
- `send_fallocate()`
- `send_verity()`

## Full vs Incremental Send

`send_subvol()` emits the stream header unless omitted, emits the initial `SUBVOL` or `SNAPSHOT` command via `send_subvol_begin()`, then chooses:

- `full_send_tree()` when there is no parent root.
- `btrfs_compare_trees()` when doing incremental send against a parent root.

`send_subvol_begin()` includes root path, UUID or received UUID, ctransid, and parent clone UUID/ctransid for incremental sends.

## Tree Comparison

`btrfs_compare_trees()` compares the send root and parent root commit trees.

Its strategy:

- Walk both B-trees in key order.
- At leaves, compare keys and item contents.
- For matching internal nodes with identical blockptr and generation, skip shared subtrees.
- Clone root nodes and leaf buffers before dropping `commit_root_sem`, so callbacks can write to the stream without holding the semaphore.
- Use readahead for newer left-root nodes.
- Detect block group relocation via `last_reloc_trans` and restart searches through `restart_after_relocation()`.

`changed_cb()` receives each new/deleted/changed/same item and dispatches by key type:

- `BTRFS_INODE_ITEM_KEY` -> `changed_inode()`
- inode refs/extrefs -> `changed_ref()`
- xattrs -> `changed_xattr()`
- file extents -> `changed_extent()`
- fs-verity descriptor item -> `changed_verity()`

For `BTRFS_COMPARE_TREE_SAME`, it may still treat refs as changed if the containing directory changed, and may still send holes for unchanged extent items.

## Inode Lifecycle

`changed_inode()` initializes current inode state and handles these cases:

- New inode.
- Deleted inode.
- Changed inode.
- Inode generation changed, meaning the inode number was reused.
- Orphan inode with `nlink == 0`.

For generation reuse, it processes the old inode as deleted, then the new inode as newly created, including all refs, extents, and xattrs.

`finish_inode_if_needed()` finalizes the previous inode before moving to the next one. It:

- Processes recorded refs.
- Advances `send_progress` when safe.
- Emits pending holes and truncation for regular files.
- Emits ownership, mode, file attributes, verity, capabilities, and utimes as needed.
- Applies child directory moves waiting on the current directory.
- Delays directory utimes for non-empty directories through `dir_utimes_cache`.

## Reference and Directory Move Handling

Incremental send has complex rename ordering requirements. The file records inode refs first, then processes them together.

Important data structures:

- `struct recorded_ref`: a new/deleted reference with directory, generation, full path, basename, rb-tree linkage.
- `struct pending_dir_move`: delayed directory rename/move keyed by parent inode.
- `struct waiting_dir_move`: reverse index for directories waiting for an ancestor move.
- `struct orphan_dir_info`: directories pending removal once children are processed.

Important functions:

- `record_new_ref_if_needed()`
- `record_deleted_ref_if_needed()`
- `record_changed_ref()`
- `process_recorded_refs()`
- `orphanize_inode()`
- `can_rmdir()`
- `wait_for_dest_dir_move()`
- `wait_for_parent_move()`
- `apply_dir_move()`
- `apply_children_dir_moves()`

The implementation handles cases where:

- A new reference would overwrite an unprocessed inode.
- The overwritten ref is the first ref, requiring orphanization.
- Directory renames depend on ancestors with higher inode numbers.
- A directory cannot be removed until children with higher inode numbers are processed.
- A destination name is still occupied by a directory whose own move is delayed.
- Cached paths must be refreshed after an ancestor was orphanized.

The temporary orphan names have the form `o<ino>-<gen>-<idx>` and are checked for uniqueness in both send and parent roots.

## Xattrs and Capabilities

Xattr processing uses `iterate_dir_item()` over `BTRFS_XATTR_ITEM_KEY` items.

Flows:

- New xattrs are emitted with `SET_XATTR`.
- Deleted xattrs are emitted with `REMOVE_XATTR`.
- Changed xattrs compare data and emit only when needed.
- Empty POSIX ACL xattrs are converted to a dummy ACL header with only the ACL version.
- Capability xattrs are skipped during normal xattr iteration and emitted later by `send_capabilities()` after ownership/mode updates.

This ordering prevents capabilities from being invalidated by later chown/chmod operations.

## fs-verity

Protocol v3 adds `BTRFS_SEND_C_ENABLE_VERITY`.

`changed_verity()` marks the current inode as needing verity when a new verity descriptor item appears. `process_verity()` loads the inode, fetches the fs-verity descriptor, validates descriptor size, and emits:

- hash algorithm
- block size
- salt
- signature

The public protocol only enables v3 when `CONFIG_BTRFS_EXPERIMENTAL` selects stream version 3 in `send.h`.

## File Data, Holes, Clones, and Compression

Extent processing starts in `process_extent()`.

Major paths:

- Skip symlink extents.
- Skip unchanged extents in incremental sends.
- Skip unsupported prealloc extents as data.
- Detect holes that must be sent in incremental sends.
- Try cloning via `find_extent_clone()`.
- Fall back to writes via `send_extent_data()`.

Clone logic:

- `find_extent_clone()` uses backref walking to locate clone candidates in allowed clone roots.
- The send root is also a clone root, but only ranges already sent to the receiver are allowed.
- Extents with more than `SEND_MAX_EXTENT_REFS` refs fall back to writes to avoid expensive backref walks.
- `backref_cache` maps leaf bytenr to clone root IDs and is invalidated after relocation.
- `clone_range()` validates source extent layout and may split a range into clone/write pieces.
- It avoids invalid EOF-block clone cases and zero-offset sectorsize clone hazards.

Data writes:

- `put_file_data()` reads from the current inode mapping using folios and readahead.
- `send_extent_data()` chunks writes by `max_send_read_size()`.
- If the page cache was initially empty, it evicts read pages after sending to reduce cache pollution.
- `BTRFS_SEND_FLAG_NO_FILE_DATA` emits `UPDATE_EXTENT` instead of actual data.

Holes:

- Protocol v2+ uses `FALLOCATE` with `PUNCH_HOLE | KEEP_SIZE`.
- Protocol v1 writes zero buffers unless `NO_FILE_DATA` is set.
- EOF and parent-hole checks avoid unnecessary writes.

Compressed data:

- With `BTRFS_SEND_FLAG_COMPRESSED` and protocol v2+, compressed extents may be emitted as `ENCODED_WRITE`.
- Inline compressed extents use `send_encoded_inline_extent()`.
- Regular compressed extents use `send_encoded_extent()` and read encoded disk bytes directly into the send buffer pages.
- The code falls back to decoded writes when compressed data is larger than the requested unencoded range.

## Relocation and Commit Root Safety

The file is careful about commit roots and relocation:

- Send roots are read-only, but block group relocation can rewrite file extent disk bytenrs.
- `last_reloc_trans` detects relocation commits.
- Full send and compare-tree paths restart searches after relocation.
- Backref cache is cleared when relocation has occurred.
- Leaf clones let callbacks safely use item buffers after releasing `commit_root_sem`.
- Holding `commit_root_sem` while writing to a pipe/file is avoided to prevent deadlocks with receive or writes on the same filesystem.

## Caches

The file uses several bounded LRU caches:

- `name_cache`: inode/generation to parent/name lookup results.
- `backref_cache`: leaf to clone-root IDs for backref walking.
- `dir_created_cache`: tracks directories created out of inode order.
- `dir_utimes_cache`: delays directory utimes and is trimmed periodically.

The caches are optimizations except where delayed utimes ordering is semantically important.

## Error Handling and Integrity Checks

The implementation uses:

- `WARN_ON`, `ASSERT`, and critical/warn/error logging for impossible states.
- `-EUCLEAN` for filesystem structure corruption.
- `-EIO` for inconsistent snapshots or read failures.
- `-ENOENT` as common “not found/fallback” signal.
- `-EOPNOTSUPP`, `-EPROTO`, `-EINVAL`, `-EPERM`, `-EAGAIN` for ioctl validation.
- CRC32C over every command.

`inconsistent_snapshot_error()` reports cases where compare-tree finds changes for an inode without the expected inode item update.

## Dependencies

This file depends heavily on Btrfs internals:

- `ctree.h`, `accessors.h`, `disk-io.h`, `transaction.h`
- inode/ref/xattr/dir item helpers
- backref walking
- compression and encoded I/O helpers
- fs-verity integration
- Btrfs LRU cache utility
- VFS file writing and page-cache/folio APIs

## Key Invariants

- The send root must be read-only for the duration of send.
- Parent and clone roots must be read-only and free of active dedupe.
- Receiver-visible path computation is governed by `send_progress`.
- Directory move ordering must avoid cycles and stale path components.
- `BTRFS_SEND_A_DATA` must be the final attribute in a command.
- Clone sources from the send root must refer only to already-emitted data.
- Relocation can stale extent disk bytenrs, so searches/cache must restart or fall back.
- Capability xattrs are emitted after ownership/mode changes.

## Research Notes

This file is not just a serializer. It is a receiver-state reconstruction engine that must output a valid linear command stream for graph-like filesystem changes. The hardest parts are directory rename ordering, orphan temporary names, clone selection under snapshot sharing, and avoiding stale metadata/data references during relocation.
