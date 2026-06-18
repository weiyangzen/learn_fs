# File Research: sources/os/linux/linux-stable/fs/btrfs/reflink.c

## Purpose

Implements Btrfs file range remapping: clone/reflink and dedupe. It is the filesystem-specific backend for `remap_file_range`, handling Btrfs extent items, inline extents, ordered extents, delalloc, locking, fsync safety, and page-cache invalidation.

Main exported entry point: `btrfs_remap_file_range()`.

## Clone Completion

`clone_finish_inode_update()` finalizes a clone transaction by:

- Incrementing inode version.
- Updating mtime/ctime unless suppressed.
- Extending `i_size` if needed.
- Resetting safe disk i_size tracking.
- Updating the inode item.
- Ending or aborting the transaction.

It caps EOF growth to the user-requested clone length rather than the block-rounded internal length.

## Inline Extent Handling

Inline extents require special handling because they cannot always be represented as shared extent references in the destination.

`copy_inline_to_page()` copies or decompresses inline data into a destination folio and marks the range delalloc/dirty. It:

- Reserves delalloc space.
- Gets or creates the destination folio.
- Sets extent mapping and delalloc state.
- Sets `BTRFS_INODE_NO_DELALLOC_FLUSH` to avoid deadlock while reflink holds range locks.
- Copies uncompressed inline data or decompresses compressed inline data.
- Zero-fills the remainder of the block when inline data is shorter than a sector.
- Marks the folio uptodate, unchecked, and dirty.
- Releases space on error.

`clone_copy_inline_extent()` chooses whether to insert an inline extent directly into the destination tree or copy its data into a page:

- Inline-to-inline insertion is possible only at destination offset 0 and when file-size constraints allow.
- Otherwise data is copied to the page cache via `copy_inline_to_page()`.
- It carefully releases Btrfs paths before starting transactions or reserving space to avoid lockdep issues and deadlocks.
- If copied beyond EOF, it updates `i_size` before starting a transaction to avoid flush-on-commit deadlocks.

## Main Clone Engine

`btrfs_clone()` clones a range from source inode to destination inode.

Flow:

1. Allocate a temporary leaf-sized buffer and Btrfs path.
2. Search source file extent items starting at `off`.
3. Include a previous overlapping extent if the first search lands after `off`.
4. Iterate extent items until the requested aligned range is covered.
5. For regular/prealloc extents:
   - Trim leading/trailing parts outside the clone range.
   - Build `btrfs_replace_extent_info`.
   - Call `btrfs_replace_file_extents()` on the destination range.
6. For inline extents:
   - Validate inline assumptions.
   - Use `clone_copy_inline_extent()`.
7. Update `last_reflink_trans` for source/destination when needed for fsync correctness.
8. Finish inode update per cloned extent.
9. Replace trailing implicit holes if no-hole or mixed I/O behavior leaves gaps.

The function handles implicit holes by dropping/replacing destination ranges even when the source has no explicit hole extent item.

## Dedupe Path

`btrfs_extent_same()` implements dedupe after the VFS has confirmed byte equality.

It prevents dedupe into a root with send operations in progress by checking and incrementing `dedupe_in_progress`.

Large dedupe requests are split into `BTRFS_MAX_DEDUPE_LEN` chunks, currently 16 MiB, using `btrfs_extent_same_range()` for each chunk. Each range locks the destination extent range and calls `btrfs_clone()` with `no_time_update = true`.

## Clone File Path

`btrfs_clone_files()` performs non-dedupe clone work:

- Rounds the source EOF block when cloning through EOF.
- Expands destination holes if cloning beyond current destination size via `btrfs_cont_expand()`.
- Waits for ordered extents after expansion to avoid racing with extent reference increments.
- Locks the destination extent range.
- Calls `btrfs_clone()`.
- Waits for ordered extents in the destination range.
- Invalidates destination page cache so future reads see cloned data.
- Balances dirty btree state.

## Remap Preparation

`btrfs_remap_file_range_prep()` validates and prepares the operation before clone/dedupe:

- Rejects clone into read-only roots.
- Requires encrypted status to match between source and destination.
- Rejects mixing `NODATASUM` and checksummed inodes.
- Flushes source file mapping to force NOCOW buffered writes to disk before increasing extent references.
- Waits for ordered ranges on source and destination.
- Delegates final generic checks to `generic_remap_file_range_prep()`.

The function intentionally does Btrfs-specific writeback and ordered-extent waiting because generic VFS preparation is insufficient for compression, ordered extent completion, and NOCOW safety.

## Locking

`btrfs_remap_file_range()` locks:

- Same inode: `btrfs_inode_lock(..., BTRFS_ILOCK_MMAP)`.
- Different inodes: `lock_two_nondirectories()` plus ordered double `i_mmap_lock` acquisition via `btrfs_double_mmap_lock()`.

Range locking is performed around clone/dedupe modifications to serialize with readahead and protect against relocation/concurrency assumptions.

## Sync Semantics

`file_sync_write()` detects `O_SYNC`, `O_DSYNC`, or inode `S_SYNC`.

After a successful remap, if either file is sync-write, `btrfs_remap_file_range()` fsyncs both source and destination ranges so reflinked data remains readable from both after power loss.

## Error Handling

The file is careful to:

- Abort transactions on metadata update failures.
- Release paths before operations that may allocate, reserve, or start transactions.
- Clear `BTRFS_INODE_NO_DELALLOC_FLUSH` on clone exit.
- Return negative errors from validation, writeback, ordered range waits, page-cache invalidation, and transaction operations.
- Return the remapped length on success.

## External Interface

`btrfs_remap_file_range()` accepts source/destination files, offsets, length, and remap flags. It supports:

- `REMAP_FILE_DEDUP`
- `REMAP_FILE_ADVISORY`

Any other flag is rejected with `-EINVAL`.
