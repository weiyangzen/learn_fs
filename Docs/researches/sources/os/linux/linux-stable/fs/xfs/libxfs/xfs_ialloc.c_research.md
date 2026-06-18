# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc.c

## Role in the repository

`xfs_ialloc.c` implements XFS inode allocation, inode freeing, inode record conversion and validation, inode chunk initialization, inode-to-buffer mapping, AGI logging and verification, inode count queries, inode allocation geometry setup, root inode prediction, and shrink safety checks.

It coordinates the AGI header, INOBT, optional FINOBT, free-space allocator, rmap ownership, superblock inode counters, per-AG cached counters, transactions, and health reporting.

## INOBT record access and validation

`xfs_inobt_lookup`, `xfs_inobt_update`, `xfs_inobt_btrec_to_irec`, `xfs_inobt_rec_freecount`, `xfs_inobt_check_irec`, `xfs_inobt_get_rec`, and `xfs_inobt_insert_rec` provide the core record access layer.

The code converts between on-disk full and sparse inode record formats. On filesystems without sparse inodes, records are treated as full chunks with a synthetic full count and zero holemask. On sparse filesystems, holemask and count fields are taken from disk.

Record validation checks AG inode range validity, count bounds, freecount bounds, and consistency between the free bitmap and freecount. Corrupt records mark the relevant btree sick and return `-EFSCORRUPTED`.

## Inode chunk initialization

`xfs_ialloc_inode_init` formats newly allocated inode clusters. For v3 inodes it writes inode numbers, metadata UUIDs, CRCs, and logs the initialization as an inode-create intent so recovery can replay logical initialization while inode buffers are tracked as ordered buffers. For v2 inodes it logs inode core ranges directly.

Without a transaction, such as during recovery-style paths, initialized inode buffers are queued for delayed write instead of being transaction-logged.

## Sparse inode record handling

Sparse inode helpers align sparse allocations to full chunk boundaries and merge records over time:
- `xfs_align_sparse_ino` aligns start inode and allocation mask.
- `__xfs_inobt_can_merge` validates compatible sparse records.
- `__xfs_inobt_rec_merge` merges holemask, count, freecount, and free mask.
- `xfs_inobt_insert_sprec` inserts or merges sparse records into INOBT.
- `xfs_finobt_insert_sprec` inserts or replaces the matching FINOBT record.

A failed sparse merge is treated as serious corruption because mount-time geometry should prevent overlapping incompatible sparse records.

## Allocating inode chunks

`xfs_ialloc_ag_alloc` allocates a new inode chunk in an AG when no free inodes are available. It first tries to extend from `agi_newino`, then tries aligned near-root allocation, then falls back to sparse allocation if supported and necessary.

After block allocation it initializes inode buffers, inserts INOBT and optional FINOBT records, updates AGI inode/free counts, updates per-AG counters, logs AGI fields, and adjusts superblock inode counters.

The allocator accounts for maximum inode count limits, stripe alignment, cluster alignment, sparse inode alignment, AG boundaries, and btree split reservation space.

## Allocating individual inodes

`xfs_dialloc` is the top-level disk inode allocator. It chooses a starting AG based on parent inode, directory rotor, and metadata-directory placement. It scans AGs, first with trylock behavior and, near low space, preferring existing free inodes before allocating new chunks.

`xfs_dialloc_try_ag` reads and locks the AGI, allocates a new inode chunk if needed, rolls the transaction while holding the AGI buffer, and allocates one inode from the selected AG.

`xfs_dialloc_ag` uses FINOBT when available, otherwise falls back to `xfs_dialloc_ag_inobt`. The FINOBT path finds a chunk near the parent or near `agi_newino`, removes or updates the FINOBT record, verifies and mirrors the change into INOBT, updates AGI/per-AG/superblock free counts, and checks counts. The INOBT-only path searches near the parent within a bounded distance, then falls back to the last allocated chunk and finally a full AG scan.

If an AG has sick inode state, candidate inodes are mapped and read before allocation to avoid reusing corrupt inode buffers.

## Freeing inodes

`xfs_difree` validates that the inode belongs to the supplied per-AG, reads the AGI, updates INOBT via `xfs_difree_inobt`, and updates FINOBT via `xfs_difree_finobt` when present.

`xfs_difree_inobt` marks the inode bit free. If the whole chunk becomes free and the block size does not contain multiple chunks, it deletes the INOBT record, updates inode/free counts, records chunk deletion details in `struct xfs_icluster`, and schedules the inode chunk blocks for freeing. Sparse chunks are freed extent-by-extent according to allocated holemask ranges.

`xfs_difree_finobt` independently updates or inserts the FINOBT record, checks consistency with the updated INOBT record, and deletes the FINOBT record when a fully free chunk is removed.

## Inode mapping

`xfs_imap` maps an inode number to disk address, buffer length, and byte offset. Trusted inode numbers can often be mapped arithmetically from inode geometry. Untrusted inode numbers, unaligned chunk layouts, and sparse layouts require `xfs_imap_lookup`, which consults INOBT and verifies that the record exists and that the inode is allocated when requested.

The final mapping is checked against filesystem block bounds before returning.

## AGI logging and verification

`xfs_ialloc_log_agi` logs AGI fields in two logical regions to avoid unnecessarily logging the large unlinked inode hash table when fields on both sides are modified.

`xfs_agi_verify`, read/write verifiers, and `xfs_agi_buf_ops` validate AGI magic, version, UUID, LSN, AG length, INOBT/FINOBT levels, and unlinked inode bucket values. Read failures from corruption or bad CRC mark AGI health sick.

`xfs_read_agi` reads an AGI buffer with verifier ops, sets buffer type and reference, and marks AGI sick on metadata errors. `xfs_ialloc_read_agi` initializes per-AG cached inode counters and optionally returns the locked buffer.

## Counting and geometry helpers

`xfs_ialloc_has_inodes_at_extent` classifies a block extent as empty, full, or sparse with respect to physically allocated inode records. `xfs_ialloc_count_inodes` walks all INOBT records to count total and free inodes.

`xfs_ialloc_setup_geometry` initializes inode geometry: new inode flags2, AG inode bit widths, INOBT fanout/minimums, inode chunk size, sparse minimum allocation size, max btree levels, maximum inode count, cluster buffer sizing, cluster alignment, stripe alignment, and minimum folio order.

`xfs_ialloc_calc_rootino` predicts the root inode location laid out by mkfs by accounting for AG headers, btree roots, AGFL, optional FINOBT/RMAPBT/refcount roots, internal log placement, and inode alignment.

`xfs_ialloc_check_shrink` prevents shrink operations from creating sparse inode records that extend beyond the new end of AG.

## Important invariants

- INOBT and FINOBT records must agree wherever both contain a chunk; FINOBT omits fully allocated chunks.
- AGI counts, per-AG counters, and superblock counters must be updated in the same transaction protocol as btree changes.
- Sparse inode records are aligned to full inode chunk ranges even if only part of the chunk is physically allocated.
- Freecount must match the actual free bits after masking out sparse holes.
- AGI logging must avoid overlogging the unlinked bucket table.
- Untrusted inode numbers require INOBT validation, not just arithmetic mapping.
