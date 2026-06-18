# File Research: sources/local-fs/btrfs-linux/fs/btrfs/send.c

## Purpose

`send.c` is the kernel implementation of Btrfs send stream generation. It turns a read-only subvolume snapshot, optionally relative to a read-only parent snapshot and clone sources, into a serialized command stream consumed by `btrfs receive`. It handles full sends, incremental sends, clone detection, data emission, directory rename ordering, xattrs, file attributes, compressed encoded writes, holes, fs-verity, stream protocol negotiation, and ioctl-level lifetime/permission checks.

The file is intentionally self-contained and stateful: most operation flows through `struct send_ctx`, which tracks protocol settings, output buffering, current inode state, compare-tree paths, pending references, rename dependencies, clone roots, page-cache read state, and several bounded LRU caches.

## Main Entry Point

`btrfs_ioctl_send()` is the exported ioctl implementation.

Key responsibilities:
- Requires `CAP_SYS_ADMIN`.
- Requires the send root, parent root, and clone roots to be read-only and not dead.
- Rejects roots with dedupe in progress, because dedupe can mutate otherwise read-only trees in ways send cannot tolerate.
- Increments `send_in_progress` on every root used by send and rolls those counters back on every exit path.
- Validates clone source count against an 8 MiB allocation cap.
- Validates `BTRFS_SEND_FLAG_MASK`.
- Chooses protocol version:
  - Without `BTRFS_SEND_FLAG_VERSION`, defaults to protocol v1.
  - With the flag, version `0` means highest supported version.
  - Rejects requested versions newer than `BTRFS_SEND_STREAM_VERSION`.
  - Requires protocol v2 or newer for `BTRFS_SEND_FLAG_COMPRESSED`.
- Opens and validates the output file descriptor for write mode.
- Allocates the send buffer:
  - v1: `BTRFS_SEND_BUF_SIZE_V1`.
  - v2+: `BTRFS_SEND_BUF_SIZE_V2` plus page pointers for direct encoded-read filling.
- Imports clone source root IDs from userspace, resolves them to roots, appends the send root as an implicit clone source, and sorts clone roots by root ID for later `bsearch()`.
- Flushes delalloc and ensures commit roots are current before sending.
- Emits the stream via `send_subvol()`, drains delayed directory utime updates, optionally emits `BTRFS_SEND_C_END`, then frees all pending state.

## Stream Command Encoding

Command assembly uses:
- `send_header()` for the stream magic/version header.
- `begin_cmd()` to reserve and initialize `struct btrfs_cmd_header`.
- `tlv_put*()` helpers and `TLV_PUT_*` macros to append attributes.
- `put_data_header()` for `BTRFS_SEND_A_DATA`.
- `send_cmd()` to finalize length, compute CRC32C, write to the output file, and reset command state.

Protocol-sensitive behavior:
- Since protocol v2, `BTRFS_SEND_A_DATA` is encoded as a type-only header and is implicitly the final command payload.
- `sctx->put_data` prevents appending normal TLVs after data.
- `proto_cmd_ok()` gates features by protocol max command:
  - v1 through `BTRFS_SEND_C_MAX_V1`.
  - v2 through `BTRFS_SEND_C_MAX_V2`.
  - v3 through `BTRFS_SEND_C_MAX_V3`.

## Path Handling

`struct fs_path` is a compact dynamic path builder with an inline buffer sized to keep the whole object at 256 bytes. It supports:
- Normal append-at-end paths.
- Reversed paths that prepend components efficiently while walking parent references upward.
- Dynamic growth through `fs_path_ensure_buf()`, rounded to kmalloc buckets.
- Conversion from reversed to normal with `fs_path_unreverse()`.

Important path functions:
- `get_inode_path()` retrieves the first resolved path for an inode.
- `get_first_ref()` retrieves an inode’s first parent directory and name.
- `get_cur_path()` computes the path an inode should have at the current logical point in the receive stream, accounting for already processed inodes, future inodes, overwritten refs, orphan names, delayed directory moves, and pending removals.
- `gen_unique_name()` creates orphan names like `o<ino>-<gen>-<idx>` and checks uniqueness in send and parent roots.

## Inode and Reference State

`get_cur_inode_state()` classifies an inode/generation pair as:
- unchanged,
- will create,
- did create,
- will delete,
- did delete.

This state drives path selection and ordering. `is_inode_existent()` treats the subvolume root as always existent and otherwise maps the state into the “currently visible at receiver” view.

References are recorded in `struct recorded_ref` lists and rbtrees:
- `new_refs`
- `deleted_refs`
- `rbtree_new_refs`
- `rbtree_deleted_refs`

The record logic cancels matching new/deleted refs against each other and defers actual link/unlink/rename decisions until `process_recorded_refs()`.

## Directory Rename and Orphan Handling

The most complex subsystem is directory move ordering. The send stream must be valid when replayed sequentially, but incremental snapshots can reorder parent/child directory relationships in ways that inode-number order cannot emit directly.

State structures:
- `struct pending_dir_move`: delayed directory move keyed by parent inode.
- `struct waiting_dir_move`: reverse index for directories waiting on parent moves.
- `struct orphan_dir_info`: tracks directories that cannot yet be removed.
- `name_cache_entry`: caches current name/parent lookups, with invalidation when entries become stale after progress advances or orphanization occurs.

Key behaviors:
- `orphanize_inode()` renames an inode to a generated orphan name before its current name would be overwritten or before a non-empty directory can be removed.
- `will_overwrite_ref()` detects whether a new ref would overwrite a currently existing parent-root ref.
- `did_overwrite_ref()` and `did_overwrite_first_ref()` detect refs already overwritten by earlier stream operations.
- `wait_for_parent_move()` delays a directory rename if an ancestor with a higher inode number must move first.
- `wait_for_dest_dir_move()` delays a rename if the destination name is occupied by another directory whose own delayed move must happen first.
- `apply_dir_move()` performs a delayed rename when dependencies are satisfied, then retries any rmdir that had been waiting on it.
- `apply_children_dir_moves()` walks pending child moves after the current directory is finalized.
- `can_rmdir()` determines whether a deleted directory’s children have all been processed; if not, it records progress in `orphan_dirs`.

This logic lets send produce valid streams for difficult cases such as directory ancestry reversals, cross-renames, delayed parent creation, and name collisions involving unprocessed inodes.

## Subvolume Begin

`send_subvol_begin()` emits either:
- `BTRFS_SEND_C_SUBVOL` for full send, or
- `BTRFS_SEND_C_SNAPSHOT` for incremental send.

It looks up the root backref name, emits path, UUID, ctransid, and, for snapshots, clone UUID/ctransid for the parent. It prefers `received_uuid` when present so streams remain portable across receive-derived subvolumes.

## Metadata Commands

The file emits common metadata commands through small wrappers:
- `send_truncate()`
- `send_chmod()`
- `send_fileattr()` for protocol v2+ file attribute state.
- `send_chown()`
- `send_utimes()`
- `send_create_inode()` for `MKFILE`, `MKDIR`, `MKNOD`, `MKFIFO`, `MKSOCK`, and `SYMLINK`.
- `send_link()`, `send_unlink()`, `send_rmdir()`, and `send_rename()`.

Directory utimes are delayed through `dir_utimes_cache` to avoid emitting timestamps before later entries are added or before delayed directory moves settle. The cache is trimmed after inode finalization and fully drained before end-of-stream.

## Xattrs, Capabilities, and ACL Quirk

Xattr handling uses `iterate_dir_item()` over `BTRFS_XATTR_ITEM_KEY` items:
- New xattrs emit `BTRFS_SEND_C_SET_XATTR`.
- Deleted xattrs emit `BTRFS_SEND_C_REMOVE_XATTR`.
- Changed xattrs compare name/data against the parent snapshot.

Special cases:
- `security.capability` is skipped during normal xattr processing and emitted later by `send_capabilities()`, after ownership/mode updates.
- Empty POSIX ACL xattrs are converted into a dummy ACL header containing only the ACL version, because receiving a zero-byte ACL would fail.

## Fs-Verity

Protocol v3 adds fs-verity support:
- `changed_verity()` marks the current inode as needing verity when a new verity descriptor item appears.
- `process_verity()` opens the Btrfs inode, obtains the fs-verity descriptor, and calls `send_verity()`.
- `send_verity()` emits `BTRFS_SEND_C_ENABLE_VERITY` with algorithm, block size, salt, and signature.

This is gated by `proto_cmd_ok(sctx, BTRFS_SEND_C_ENABLE_VERITY)`.

## File Data, Holes, Clones, and Encoded Writes

Data emission supports several modes:
- `send_write()` sends normal file data.
- `send_update_extent()` emits extent update metadata when `BTRFS_SEND_FLAG_NO_FILE_DATA` is set.
- `send_clone()` emits clone commands from parent/clone/send roots.
- `send_fallocate()` emits protocol v2 fallocate commands.
- `send_hole()` emits hole punching via fallocate on v2+, or zero writes / update extent fallback on v1.
- `send_encoded_inline_extent()` and `send_encoded_extent()` emit compressed encoded writes when `BTRFS_SEND_FLAG_COMPRESSED` is set and the compressed representation is no larger than the unencoded range.

`put_file_data()` reads file pages through the page cache with readahead. If the inode mapping was initially empty, `send_extent_data()` marks the cache as cleanable and later truncates page-cache ranges to avoid polluting global cache with send-only reads.

Clone discovery:
- `find_extent_clone()` uses backref walking to find usable clone sources.
- It skips the current unprocessed destination range.
- It avoids clone sources later than the current send position.
- It caches leaf-to-root backref results in `backref_cache`.
- It invalidates the cache after block group relocation.
- It refuses clone attempts for extents with more than `SEND_MAX_EXTENT_REFS` references.

`clone_range()` validates that a clone source range still maps to the expected disk extent, handles holes and mismatches by falling back to writes, avoids problematic sector-size and EOF clone cases, and splits clone/write ranges as needed.

## Extent Change Detection

`is_extent_unchanged()` compares a left/send extent against parent-root extents. It handles:
- matching regular extents,
- split extents,
- holes,
- inline extents as changed,
- extent offsets and generation checks.

`maybe_send_hole()` detects holes newly introduced relative to the parent snapshot and emits them if needed. `need_send_hole()` limits this to regular files in incremental sends where the inode is not new, not deleted, and not a new generation.

## Compare-Tree Engine

Incremental send uses `btrfs_compare_trees()`:
- Compares send root and parent root commit trees.
- Skips shared subtrees when block pointer and generation match.
- Clones root nodes and leaves to safely release `commit_root_sem` before calling callbacks that may write to the output file.
- Drops and reacquires `commit_root_sem` to avoid deadlocks with receive-on-same-filesystem or output files stored on the same filesystem.
- Restarts after block group relocation to avoid stale extent buffers or stale pre-relocation disk bytenrs.
- Calls `changed_cb()` with `NEW`, `DELETED`, `CHANGED`, or `SAME`.

Full send uses `full_send_tree()`:
- Walks the send root from `BTRFS_FIRST_FREE_OBJECTID`.
- Treats every item as new.
- Also restarts lookup after relocation.

`changed_cb()` first finalizes any previous inode, ignores non-filesystem objects, dispatches inode/ref/xattr/extent/verity items, and upgrades some `SAME` ref/extent cases into changed work when parent directory generation or holes require it.

## Inode Finalization

`finish_inode_if_needed()` is the per-inode flush point. It:
- Processes pending recorded refs.
- Advances `send_progress` when safe.
- Emits trailing holes and truncates regular files as needed.
- Emits chown, chmod, fileattr, fs-verity, capabilities, child directory moves, and utimes.
- Defers non-empty directory utimes.
- Trims delayed utime cache.

`changed_inode()` initializes `send_ctx` state for a new current inode and handles:
- normal new/deleted/changed inode items,
- generation changes as delete plus create,
- root directory special handling,
- orphan inode cases with zero link count,
- creation of new inodes under orphan names before references are processed.

## Concurrency and Consistency Assumptions

Important invariants:
- Send roots, parent roots, and clone roots must be read-only.
- Dedupe is blocked during send because it can mutate read-only roots.
- Delalloc is flushed before commit roots are used.
- Commit roots are made current after orphan cleanup or delalloc flushing.
- `commit_root_sem` is not held while writing to userspace/output, preventing deadlocks.
- Relocation generation checks protect against stale metadata or stale disk addresses.
- `send_in_progress` protects roots against mode changes/deletion while send is active.

## Error Handling and Cleanup

The file uses kernel error codes consistently:
- `-EPERM` for permission/read-only/root-dead violations.
- `-EAGAIN` for dedupe-in-progress conflicts.
- `-EINVAL`, `-EOPNOTSUPP`, `-EPROTO`, `-EBADF`, `-EFAULT`, `-ENOMEM`, `-EIO`, `-EUCLEAN`, and `-ENAMETOOLONG` in their local contexts.

Cleanup is centralized in `btrfs_ioctl_send()`:
- Frees pending directory moves, waiting moves, orphan dir records.
- Decrements `send_in_progress`.
- Drops root refs and file refs.
- Frees send buffers, page arrays, clone roots, verity descriptor, path buffers, and LRU caches.
- Calls `close_current_inode()` to drop inode references and clear any remaining page-cache range selected for cleanup.

## Dependencies

Internal Btrfs dependencies include tree search/walk, inode items, dir items, file extents, backrefs, transactions, compression/encoded IO, fs-verity support, LRU caches, extent buffers, relocation generation tracking, and root item state. Linux dependencies include xattrs, POSIX ACL encoding, file writes, page cache/folios/readahead, fallocate flags, capabilities, compat types, CRC32C, vmalloc/kvmalloc, rbtrees, and sorting/search helpers.

## Research Notes

This file is the authoritative kernel-side stream producer. The important design point is that it does not merely diff two trees; it simulates a receive-side timeline. `send_progress`, orphan names, path recomputation, delayed directory moves, and delayed utimes all exist to ensure every emitted command is valid at the exact point it is replayed by `btrfs receive`.
