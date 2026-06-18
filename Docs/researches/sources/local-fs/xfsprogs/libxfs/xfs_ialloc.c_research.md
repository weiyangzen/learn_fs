# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ialloc.c

## Purpose
Implements XFS inode allocation, inode freeing, inode mapping, AGI logging/verification, inode allocation geometry setup, inobt record validation/counting, sparse inode handling, and shrink safety checks.

## Main Functional Areas
- Inobt record operations:
  - `xfs_inobt_lookup` sets cursor search key and calls generic btree lookup.
  - `xfs_inobt_update` serializes incore records to ondisk format, respecting sparse inode feature support.
  - `xfs_inobt_btrec_to_irec` converts ondisk records into normalized incore form.
  - `xfs_inobt_rec_freecount` calculates real free inode count, masking out sparse holes.
  - `xfs_inobt_check_irec` validates start/end agino bounds, count limits, freecount bounds, and freecount consistency.
  - `xfs_inobt_get_rec` wraps generic record read plus validation and sickness marking.
  - `xfs_inobt_insert_rec` inserts the current cursor record.
- New inode chunk initialization:
  - `xfs_ialloc_inode_init` zeroes inode buffers, stamps magic/version/generation/unlinked state, sets v3 inode number and UUID, calculates CRCs, and logs or delayed-writes buffers depending on transaction context.
  - V3 inode creation logs a logical icreate item and treats buffers as ordered allocation buffers.
- Sparse inode record handling:
  - `xfs_align_sparse_ino` aligns sparse chunks to full inode chunk boundaries and shifts allocation masks.
  - `__xfs_inobt_can_merge` and `__xfs_inobt_rec_merge` validate and merge sparse records.
  - `xfs_inobt_insert_sprec` inserts or merges sparse inobt records.
  - `xfs_finobt_insert_sprec` inserts or replaces corresponding finobt records using merged inobt state.
- Allocating inode chunks:
  - `xfs_ialloc_ag_alloc` chooses an extent for a new inode chunk.
  - Tries exact allocation after the last chunk, then near-root allocation with stripe/cluster alignment, then sparse allocation if enabled.
  - Initializes inode buffers, inserts inobt/finobt records, updates AGI counts, perag counters, and superblock counters.
  - Enforces max inode count and leaves space for btree splits.
- Allocating individual inodes:
  - `xfs_dialloc_ag_inobt` searches the inobt when finobt is unavailable, preferring parent locality and cached left/right search positions.
  - `xfs_dialloc_ag_finobt_near` finds the closest free inode record to the parent using the finobt.
  - `xfs_dialloc_ag_finobt_newino` uses AGI `agi_newino` or first free finobt record.
  - `xfs_dialloc_ag_update_inobt` mirrors finobt allocation changes into inobt and verifies both records match.
  - `xfs_dialloc_ag` dispatches finobt or inobt algorithm, updates AGI/perag/superblock free counts, and avoids sick inode clusters when possible.
  - `xfs_dialloc` picks an AG, handles low-space retry policy, tries AGs with/without trylocks, and rejects obviously corrupt allocations such as reallocating the parent inode.
- Freeing inodes:
  - `xfs_difree_inode_chunk` frees whole or sparse physical inode chunk extents.
  - `xfs_difree_inobt` marks an inode free, deletes fully free chunks when allowed, updates counters, and returns chunk deletion details via `xfs_icluster`.
  - `xfs_difree_finobt` independently mirrors the free operation in finobt, inserting/updating/deleting finobt records as required.
  - `xfs_difree` validates inode-to-AG mapping, reads AGI, updates inobt, then finobt if enabled.
- Mapping inode numbers:
  - `xfs_imap_lookup` verifies an inode number against inobt for untrusted lookups or unaligned chunks.
  - `xfs_imap` maps inode number to disk address, buffer length, and byte offset, using arithmetic fast paths when safe and btree lookup otherwise.
- AGI logging and verification:
  - `xfs_ialloc_log_agi` logs only requested AGI fields and splits ranges around the unlinked bucket region.
  - `xfs_agi_verify`, read/write verifiers, and `xfs_agi_buf_ops` validate magic, version, UUID, LSN, AG length, btree levels, and unlinked inode buckets.
  - `xfs_read_agi` reads and types AGI buffers, marking AGI sick on metadata corruption.
  - `xfs_ialloc_read_agi` initializes perag inode counters from AGI and debug-checks stale AGI/perag mismatch.
- Counting and shrink support:
  - `xfs_ialloc_has_inodes_at_extent` classifies an extent as empty/full/sparse of physical inode records.
  - `xfs_ialloc_count_inodes` sums count/freecount across all inobt records.
  - `xfs_ialloc_setup_geometry` computes inode btree record capacities, max levels, max inode count, cluster sizes, alignment, min folio order, and default new inode flags.
  - `xfs_ialloc_calc_rootino` predicts mkfs root inode placement from AG0 metadata layout.
  - `xfs_ialloc_check_shrink` prevents shrinking an AG past sparse inode records that would extend beyond the new end.

## Dependencies and Integration
- Depends heavily on:
  - `xfs_format.h` for AGI, inode, inobt, and conversion formats.
  - `xfs_ialloc_btree.c/h` for inobt/finobt cursors and allocation masks.
  - Free-space allocator APIs for inode chunk extent allocation/freeing.
  - Transaction APIs for buffer logging, rolling, superblock counter deltas, and ordered inode allocation buffers.
  - Health APIs to mark AGI/inobt/finobt/inodes sick.
  - Mount/perag geometry from `xfs_mount.h` and `xfs_ag.h`.

## Invariants
- Inobt is authoritative for all inode chunks; finobt only tracks records with at least one free inode.
- Inobt and finobt record contents must match whenever both contain a record.
- Sparse inode records require holemask-aware freecount and allocation mask handling.
- AGI `agi_count`, `agi_freecount`, perag counters, and superblock counters must be updated together.
- V3 inode initialization requires full inode CRC coverage and logical icreate logging.
- Untrusted inode lookups must validate against the inode btree before reading stale disk inodes.
- Fully free inode chunks can be removed only when block size does not pack multiple chunks into one filesystem block.

## Notable Risks
- Counter synchronization is delicate; debug checks exist because stale AGI/AGF state can imply storage write loss or corruption.
- Allocation near ENOSPC intentionally has a two-pass policy, but comments note the AG free-space precheck is imperfect with per-AG reservations.
- Sparse inode merge failure is treated as serious corruption and can force shutdown.
- `xfs_dialloc_roll` deliberately moves quota accounting across transaction roll boundaries; mishandling this could charge the wrong transaction.
- `xfs_imap` must avoid arithmetic shortcuts for untrusted or unaligned cases to prevent stale inode exposure.
