# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc.c

## Purpose

`xfs_ialloc.c` implements XFS inode allocation, freeing, inode mapping, AGI verification/logging, inode record validation, sparse inode record handling, and inode allocation geometry setup.

## Main Content

- Inobt record operations:
  - `xfs_inobt_lookup` positions an inode btree cursor.
  - `xfs_inobt_update` writes an incore inode record to the current btree record.
  - `xfs_inobt_btrec_to_irec` converts on-disk btree records to incore records.
  - `xfs_inobt_rec_freecount` computes real free inode count, accounting for sparse holes.
  - `xfs_inobt_check_irec` validates alignment, count, freecount, and free mask consistency.
  - `xfs_inobt_get_rec` retrieves and validates the current record.
  - `xfs_inobt_insert_rec` inserts one record from cursor state.
- New inode initialization:
  - `xfs_ialloc_inode_init` stamps newly allocated inode buffers.
  - V3 inodes get inode numbers, metadata UUIDs, CRCs, and logical icreate logging.
  - Older inodes log inode cores physically.
- Sparse inode support:
  - `xfs_align_sparse_ino` aligns sparse chunk records to full chunk boundaries.
  - Merge helpers detect and combine compatible sparse records.
  - `xfs_inobt_insert_sprec` inserts or merges sparse records into the inobt.
  - `xfs_finobt_insert_sprec` inserts or replaces sparse records in the finobt.
- AG inode chunk allocation:
  - `xfs_ialloc_ag_alloc` allocates a new inode chunk in an AG.
  - Tries contiguous allocation after `agi_newino`, near btree roots, stripe/cluster alignment, then sparse allocation if supported.
  - Initializes new inode buffers, inserts inobt/finobt records, updates AGI and superblock inode counters.
- Inode allocation from existing free records:
  - `xfs_dialloc_ag_inobt` implements the inobt-only allocator.
  - `xfs_dialloc_ag_finobt_near` and `xfs_dialloc_ag_finobt_newino` implement finobt search policies.
  - `xfs_dialloc_ag_update_inobt` mirrors finobt allocation into the inobt.
  - `xfs_dialloc_ag` chooses finobt or inobt path.
- AG selection and top-level allocation:
  - `xfs_dialloc_pick_ag` picks a starting AG based on metadata directory placement, directory rotor, or parent AG.
  - `xfs_dialloc_good_ag` checks AG eligibility, free inode availability, and whether enough free space exists to allocate a new inode chunk.
  - `xfs_dialloc_try_ag` reads AGI, allocates chunks if needed, rolls transactions, and allocates one inode.
  - `xfs_dialloc` scans AGs with a trylock pass and fallback pass, handles low-space behavior, enforces max inode count, and rejects obviously corrupt allocations.
- Inode freeing:
  - `xfs_difree_inode_chunk` frees full or sparse inode chunk backing extents.
  - `xfs_difree_inobt` marks an inode free, deletes a fully free chunk when eligible, updates AGI/superblock counters, and returns cluster deletion info.
  - `xfs_difree_finobt` updates, inserts, or removes the finobt record to stay consistent with the inobt.
  - `xfs_difree` validates inode-to-AG mapping, reads AGI, updates inobt, then finobt if enabled.
- Inode mapping:
  - `xfs_imap_lookup` performs btree lookup for untrusted or unaligned inode mapping.
  - `xfs_imap` maps an inode number to disk address, buffer length, and byte offset, with fast arithmetic paths for simple geometry.
- AGI logging and verification:
  - `xfs_ialloc_log_agi` logs selected AGI fields in two regions to avoid logging the whole unlinked hash table unnecessarily.
  - `xfs_agi_verify`, read/write verifiers, and `xfs_agi_buf_ops` validate AGI magic, version, UUID/LSN, AG length, btree levels, and unlinked inode buckets.
  - `xfs_read_agi` reads AGI buffers and marks AGI sick on metadata corruption.
  - `xfs_ialloc_read_agi` initializes per-AG inode counters from AGI.
- Inode accounting and extent occupancy:
  - `xfs_ialloc_has_inodes_at_extent` reports whether an extent is empty, full, or sparse with respect to inode records.
  - `xfs_ialloc_count_inodes` counts total and free inodes under an inobt.
- Geometry:
  - `xfs_ialloc_setup_geometry` derives inode btree sizes, max levels, max inode count, inode cluster size, sparse allocation minimums, alignment, and folio order.
  - `xfs_ialloc_calc_rootino` computes the mkfs-laid-out root inode location.
  - `xfs_ialloc_check_shrink` prevents shrink from cutting through sparse inode records.

## Key Interfaces and Invariants

- Inobt and finobt records must describe equivalent chunk contents, but finobt only contains chunks with at least one free inode.
- AGI free counts, per-AG cached counts, and superblock counters are updated together under transaction control.
- Fully free inode chunks can be removed only when the filesystem block geometry does not contain multiple inode chunks per block.
- Sparse inode records must be aligned to full inode chunk boundaries and must not overlap allocated ranges.
- Allocation protects against reusing the parent inode and invalid directory inode numbers before returning success.
- AGI verifiers mark metadata sick for corruption/CRC failures, integrating allocator validation with the health model.

## Dependencies

Depends heavily on:
- `xfs_format.h` for AGI layout, inode record layout, masks, and address conversions.
- `xfs_ialloc_btree.h` for cursor creation and record address geometry.
- Allocation, transaction, btree, icreate logging, buffer, rmap, per-AG, and health subsystems.
