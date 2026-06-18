# File Research: sources/os/linux/linux/fs/btrfs/reflink.c

## Scope

`reflink.c` implements Btrfs file range remapping for clone and dedupe operations. It handles VFS remap preparation, source/destination locking, extent sharing, inline extent copying, hole handling, inode updates, page-cache invalidation, writeback ordering, and synchronous-file durability behavior.

## Main Entry Point

`btrfs_remap_file_range()` validates remap flags, rejects shutdown filesystems, locks one or two inodes plus mmap locks, prepares the remap, dispatches to dedupe or clone, unlocks, and fsyncs both source and destination ranges when either file requires synchronous writes.

It returns the remapped length on success or a negative errno.

## Remap Preparation

`btrfs_remap_file_range_prep()` enforces Btrfs-specific constraints before the generic VFS helper:

- Non-dedupe clone cannot target a read-only root.
- Source and destination encryption state must match.
- Source and destination `NODATASUM` state must match.
- Source writeback is flushed to force NOCOW buffered writes to land before sharing references.
- Ordered extents are waited on for both source and destination aligned ranges.
- Then `generic_remap_file_range_prep()` performs generic overlap, EOF, dedupe comparison, and alignment checks.

## Clone Core

`btrfs_clone()` walks source file extent items from the source root and maps them into destination offsets. It handles:

- Regular and prealloc extents via `btrfs_replace_file_extents()`.
- Inline extents via `clone_copy_inline_extent()`.
- Implicit holes, including `NO_HOLES` cases, by dropping/replacing destination extents.
- Source ranges that begin in the middle of an extent.
- Destination i_size growth and inode updates after each transaction.
- `last_reflink_trans` updates to make fsync log checksums and shared extent state safely.
- Full-sync marking where hole logging would otherwise be skipped.

`clone_finish_inode_update()` increments inode version, updates timestamps when needed, adjusts i_size without over-rounding the user length, writes safe disk i_size state, updates the inode item, and ends the transaction.

## Inline Extent Handling

`clone_copy_inline_extent()` tries to preserve an inline extent in the destination when legal: destination offset 0, compatible file size, and at most one extent adjustment. Otherwise it copies inline data into a destination folio through `copy_inline_to_page()`.

`copy_inline_to_page()` reserves delalloc space, creates/locks the destination folio, maps and marks delalloc state, temporarily sets `BTRFS_INODE_NO_DELALLOC_FLUSH`, copies or decompresses inline data, zero-fills the rest of the sector, marks the folio uptodate/dirty, and releases reservation state. This avoids starting a transaction while holding locks that could deadlock with delalloc flushing.

The code has explicit deadlock avoidance for copying inline data beyond EOF before starting the inode-update transaction.

## Clone And Dedupe Wrappers

`btrfs_clone_files()` expands the destination with `btrfs_cont_expand()` if cloning beyond EOF, waits ordered writeback for the expanded tail, locks the destination extent range, calls `btrfs_clone()`, waits ordered writeback for any inline-copy delalloc, invalidates destination page cache, and balances dirty btrees.

`btrfs_extent_same()` protects against concurrent send by incrementing `dedupe_in_progress`, then dedupes in chunks of at most `BTRFS_MAX_DEDUPE_LEN` using `btrfs_extent_same_range()`. Dedupe uses `no_time_update = true`.

## Locking And Concurrency

- Same-inode remaps use `btrfs_inode_lock(..., BTRFS_ILOCK_MMAP)`.
- Cross-inode remaps use `lock_two_nondirectories()` plus ordered double mmap locking.
- Destination extent ranges are locked during clone/dedupe replacement.
- The source mmap lock protects against relocation races.
- Range writeback and ordered extent waits ensure source extents are stable and destination dirty state is not racing replacement.
- `send_in_progress` prevents dedupe from modifying roots used by send.

## Dependencies

The file relies on Btrfs transaction handling, extent replacement/drop helpers, inode item updates, delalloc reservation/accounting, compression decompression, folio/page-cache APIs, VFS remap helpers, ordered extent waiting, root send/dedupe counters, and fsync.

## Risks And Invariants

- Inline extents can only be cloned as inline at offset 0 and within sector-size limits; otherwise data must be copied to a page.
- Source and destination checksum policy must match to avoid partially checksummed files.
- NOCOW writeback must complete before increasing extent references.
- Page cache must be invalidated after clone so future reads do not see stale destination data.
- `last_reflink_trans` updates are required to avoid fsync logging overlapping checksum items incorrectly.
- Hole cloning with `NO_HOLES` may require full fsync marking when i_size changes.

## Testing Signals

Relevant coverage includes clone and dedupe across files and within one file, inline-to-inline clone, inline-to-page clone, compressed inline extents, holes with `NO_HOLES`, clone beyond EOF, unaligned EOF clone, NODATASUM mismatch, encryption mismatch, read-only roots, send-in-progress dedupe blocking, O_SYNC/O_DSYNC remaps, NOCOW buffered writes, and page-cache coherency after clone.
