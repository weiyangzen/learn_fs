# File Research: sources/local-fs/kdave-linux/fs/btrfs/reflink.c

## Purpose

`reflink.c` implements Btrfs file range cloning and deduplication through the VFS `remap_file_range` operation. It handles regular extents, prealloc extents, inline extents, implicit holes, inode size updates, ordered extent/writeback synchronization, page cache invalidation, and sync semantics.

Public entry point: `btrfs_remap_file_range()`.

## Main Operations

The file supports two remap modes:

- Clone/reflink: share source extents with the destination.
- Dedupe: verify sameness through generic VFS preparation, then share extents without updating destination times.

## Inline Extent Handling

Inline extents need special handling because Btrfs inline extents normally live only at file offset 0 and cannot be partially cloned in the same way as regular extents.

`copy_inline_to_page()` materializes inline data into a destination folio:

- Reserves delalloc space.
- Gets/creates and locks the destination folio.
- Marks extent delalloc.
- Temporarily sets `BTRFS_INODE_NO_DELALLOC_FLUSH` to avoid deadlock while ranges are locked.
- Copies or decompresses inline data into the folio.
- Zero-fills the rest of the sector if inline data is shorter than a sector.
- Marks the folio uptodate, unchecked, and dirty.
- Releases reservations on error.

`clone_copy_inline_extent()` decides whether to copy an inline extent as an inline metadata item or materialize it into a page. It directly inserts an inline item only when destination offset is 0 and destination size constraints allow it. Otherwise it calls `copy_inline_to_page()`.

The function contains explicit transaction/deadlock avoidance: it releases paths before reserving data or starting transactions, and updates i_size before starting a transaction when copying inline data beyond EOF to avoid flush-on-commit deadlock.

## Core Clone Logic

`btrfs_clone()` performs the actual range clone.

Inputs include source/destination offsets, original user length, block-aligned clone length, and whether destination mtime/ctime updates should be skipped.

Flow:

1. Allocate a path and a temporary buffer sized to `nodesize`.
2. Search the source inode’s file extent items starting at the source offset.
3. If needed, back up to a previous extent that overlaps the range.
4. Iterate extent items until the clone range is covered.
5. For regular/prealloc extents:
   - Trim leading/trailing portions outside the requested source range.
   - Fill `btrfs_replace_extent_info`.
   - Call `btrfs_replace_file_extents()` over the destination range.
6. For inline extents:
   - Validate inline constraints.
   - Delegate to `clone_copy_inline_extent()`.
7. Update `last_reflink_trans` for source/destination to keep fsync checksum logging correct.
8. Update inode metadata with `clone_finish_inode_update()`.
9. Handle trailing implicit holes with `btrfs_replace_file_extents(..., NULL, ...)`.

The function carefully tracks:

- `last_dest_end`: cloned destination coverage.
- `prev_extent_end`: source extent progress, including races with ordered extent completion.
- `drop_start`: start of destination region to drop/replace, including implicit holes.

It clears `BTRFS_INODE_NO_DELALLOC_FLUSH` on exit.

## Inode Update

`clone_finish_inode_update()`:

- increments inode version.
- updates mtime/ctime unless suppressed.
- caps EOF expansion to the original requested length.
- updates `i_size` and safe disk i_size as needed.
- calls `btrfs_update_inode()`.
- aborts transaction on inode update failure.
- ends the transaction.

## Dedupe Path

`btrfs_extent_same()` handles dedupe after VFS preparation. It increments `root_dst->dedupe_in_progress` unless send is in progress, in which case it returns `-EAGAIN`.

Dedupe work is chunked by `BTRFS_MAX_DEDUPE_LEN` (`16 MiB`) through `btrfs_extent_same_range()`.

`btrfs_extent_same_range()`:

- Locks the destination extent range.
- Calls `btrfs_clone()` with `no_time_update = true`.
- Unlocks the range.
- Balances dirty btree pages.

## Clone Path

`btrfs_clone_files()` handles non-dedupe clone:

- Expands `len` to cover the aligned EOF block when cloning to source EOF.
- If cloning beyond destination EOF, calls `btrfs_cont_expand()` and waits for ordered extents to finish over the expanded range.
- Locks the destination extent range.
- Calls `btrfs_clone()` with time updates enabled.
- Waits for ordered range completion after clone because inline data may have been copied into dirty folios.
- Invalidates destination page cache over the cloned range so future reads see cloned data.
- Balances dirty btree pages.

## Remap Preparation

`btrfs_remap_file_range_prep()` performs Btrfs-specific validation and synchronization before calling `generic_remap_file_range_prep()`.

Checks and preparation include:

- Non-dedupe clone cannot target a read-only root.
- Source and destination encryption state must match.
- Source and destination `NODATASUM` flags must match, preventing a partly checksummed destination file.
- Flush source mapping before reflink to force NOCOW buffered writes to disk as NOCOW before extent refs are increased.
- Wait for ordered extents on both source and destination aligned ranges.
- Computes writeback length carefully for full-file clone (`len == 0`) and sector alignment.

## Top-Level Entry Point

`btrfs_remap_file_range()`:

1. Rejects operation if filesystem is shut down.
2. Rejects unsupported remap flags.
3. Locks either one inode or both source/destination non-directory inodes.
4. Takes exclusive Btrfs mmap locks in stable pointer order for two-inode operations.
5. Calls Btrfs remap preparation.
6. Dispatches to dedupe or clone.
7. Unlocks inodes and mmap locks.
8. If either file is synchronous (`O_SYNC`, `O_DSYNC`, or `S_SYNC`) and the remap succeeded, fsyncs both source and destination ranges.
9. Returns cloned/deduped length or error.

## Locking and Concurrency

- `btrfs_double_mmap_lock()` locks mmap semaphores in pointer order with nested locking.
- Destination extent ranges are locked during clone/dedupe replacement.
- Ordered extents are waited before sharing references to avoid races with not-yet-created file extent items.
- Page cache invalidation happens after clone completion and ordered extent waiting.
- Send and dedupe are coordinated through `send_in_progress` and `dedupe_in_progress`.

## Important Invariants

- Reflink ranges must obey sector-size alignment rules enforced by VFS/generic prep.
- Inline extents are whole-sector/offset-0 special cases.
- Destination cannot become partly checksummed.
- Encrypted and unencrypted files cannot be reflinked together.
- Sync writes require syncing both source and destination ranges after successful remap.
